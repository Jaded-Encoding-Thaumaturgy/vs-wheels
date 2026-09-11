import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python bin2c.py <input.bin> <output.h> [var_name]")
        sys.exit(1)

    bin_path = Path(sys.argv[1])
    h_path = Path(sys.argv[2])
    var_name = sys.argv[3] if len(sys.argv) > 3 else "kernels_fatbin"

    data = bin_path.read_bytes()
    h_path.parent.mkdir(parents=True, exist_ok=True)

    with open(h_path, "w", encoding="ascii") as f:
        f.write("#pragma once\n")
        f.write("#include <stddef.h>\n\n")
        f.write(f"static const unsigned char {var_name}[] = {{\n")
        for i in range(0, len(data), 16):
            chunk = data[i : i + 16]
            hex_str = ", ".join(f"0x{b:02x}" for b in chunk)
            f.write(f"    {hex_str},\n")
        f.write("};\n\n")
        f.write(f"static const size_t {var_name}_size = sizeof({var_name});\n")

if __name__ == "__main__":
    main()
