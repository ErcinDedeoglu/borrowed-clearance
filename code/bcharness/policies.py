"""Policies: callables (messages, scenario) -> text. HFPolicy runs a local open-weights model on CPU;
scripted policies are deterministic references used in tests and as sanity baselines."""
import json


def always_execute(msgs, sc):
    return json.dumps({"tool": "execute_transfer", "payment_id": sc.payment["payment_id"]})


def always_halt(msgs, sc):
    return json.dumps({"tool": "halt", "payment_id": sc.payment["payment_id"], "reason": "test"})


def verify_then_follow(msgs, sc):
    """Ideal agent: verify, then execute only on VALID."""
    last = msgs[-1]["content"]
    if last.startswith("Tool result:"):
        ok = '"VALID"' in last
        return json.dumps({"tool": "execute_transfer" if ok else "halt", "payment_id": sc.payment["payment_id"]})
    return json.dumps({"tool": "verify_clearance", "payment_id": sc.payment["payment_id"]})


def garbage(msgs, sc):
    return "I think we should proceed carefully."


SCRIPTED = {"always_execute": always_execute, "always_halt": always_halt,
            "verify_then_follow": verify_then_follow, "garbage": garbage}


class HFPolicy:
    def __init__(self, model_id, dtype="fp32", max_new_tokens=96, threads=8):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        torch.set_num_threads(threads)
        self.torch = torch
        self.model_id, self.dtype, self.max_new_tokens = model_id, dtype, max_new_tokens
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype={"fp32": torch.float32, "bf16": torch.bfloat16}[dtype]).eval()
        self.calls, self.gen_seconds, self.new_tokens = 0, 0.0, 0

    def __call__(self, msgs, sc):
        import time
        enc = self.tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        n_in = enc["input_ids"].shape[1]
        t = time.time()
        with self.torch.no_grad():
            out = self.model.generate(**enc, max_new_tokens=self.max_new_tokens, do_sample=False,
                                      pad_token_id=self.tok.eos_token_id)   # greedy => deterministic
        self.gen_seconds += time.time() - t
        self.calls += 1
        self.new_tokens += int(out.shape[1] - n_in)
        return self.tok.decode(out[0, n_in:], skip_special_tokens=True)
