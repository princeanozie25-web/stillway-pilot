"""The v0.3 editor: a register write.  It sees the saved register IDs, the field and the new value, nothing else.
Nothing is fitted.  It abstains when the field's register was never written or the value is not a legal one."""
import torch


class RegisterWrite:
    def __call__(self, ids: torch.Tensor, field: torch.Tensor, value: torch.Tensor, obs=None):
        ar = torch.arange(len(ids)); new = ids.clone()
        abstain = (ids[ar, field] < 0) | (value < 0) | (value > 2)
        new[ar, field] = value
        return new, abstain
