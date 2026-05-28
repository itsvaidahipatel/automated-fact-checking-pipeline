"""
QLoRA fine-tuning boilerplate for claim-extraction specialization.

Trains LoRA adapters on Qwen2.5-3B-Instruct using Unsloth, then exports
weights compatible with vLLM serving.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "unsloth/Qwen2.5-3B-Instruct"
DEFAULT_OUTPUT_DIR = Path("outputs/claim-extraction-qlora")


@dataclass
class TrainConfig:
    model_name: str = DEFAULT_MODEL
    max_seq_length: int = 2048
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    learning_rate: float = 2e-4
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    max_steps: int = 300
    output_dir: Path = DEFAULT_OUTPUT_DIR
    dataset_path: Path = Path("data/claim_extraction.jsonl")


def load_dataset(path: Path) -> list[dict[str, str]]:
    """
    Load JSONL claim-extraction dataset.

    Expected schema per line:
        {"instruction": "...", "input": "<raw text>", "output": "[\"claim1\", ...]"}
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. "
            "Provide a JSONL file with instruction/input/output fields."
        )
    records: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def format_example(record: dict[str, str]) -> str:
    """Alpaca-style prompt for supervised fine-tuning."""
    return (
        f"### Instruction:\n{record['instruction']}\n\n"
        f"### Input:\n{record['input']}\n\n"
        f"### Response:\n{record['output']}"
    )


def build_trainer(cfg: TrainConfig) -> tuple[Any, Any, Any]:
    """
    Initialize Unsloth model, LoRA adapters, and TRL SFTTrainer.

    Returns:
        (model, tokenizer, trainer) tuple ready for .train()
    """
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer
    from unsloth import FastLanguageModel

    records = load_dataset(cfg.dataset_path)
    texts = [format_example(r) for r in records]
    dataset = Dataset.from_dict({"text": texts})

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg.model_name,
        max_seq_length=cfg.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    training_args = SFTConfig(
        output_dir=str(cfg.output_dir),
        per_device_train_batch_size=cfg.batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        learning_rate=cfg.learning_rate,
        max_steps=cfg.max_steps,
        logging_steps=10,
        save_steps=100,
        fp16=False,
        bf16=True,
        optim="adamw_8bit",
        report_to="none",
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=training_args,
    )
    return model, tokenizer, trainer


def export_for_vllm(model: Any, tokenizer: Any, output_dir: Path) -> None:
    """Merge LoRA weights and save in HuggingFace format for vLLM."""
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained_merged(str(output_dir), tokenizer, save_method="merged_16bit")
    logger.info("Merged model exported to %s", output_dir)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="QLoRA claim-extraction fine-tuning")
    parser.add_argument("--dataset", type=Path, default=TrainConfig.dataset_path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-steps", type=int, default=300)
    args = parser.parse_args()

    cfg = TrainConfig(dataset_path=args.dataset, output_dir=args.output_dir, max_steps=args.max_steps)
    model, tokenizer, trainer = build_trainer(cfg)
    trainer.train()
    export_for_vllm(model, tokenizer, cfg.output_dir / "merged")


if __name__ == "__main__":
    main()
