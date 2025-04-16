import os
import sys
import argparse
import torch

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch GUI")
    parser.add_argument(
        "--force-tf32",
        action="store_true",
        help="Force FP32 precision and ensure TF32 is enabled",
    )
    args = parser.parse_args()

    if torch.cuda.is_available():
        major, _ = torch.cuda.get_device_capability()
        if major >= 8:
            print("Enabling TF32")
            torch.backends.cuda.matmul.allow_tf32 = True
        else:
            print("GPU does not support TF32 (requires Ampere+ architecture).")
            torch.backends.cuda.matmul.allow_tf32 = False
    else:
        print("CUDA not available, TF32 settings not applicable.")

    if args.force_tf32:
        print("NOTE: --force-tf32 flag used")

    from gui.gui import GUI
    GUI(force_fp32=args.force_tf32)
