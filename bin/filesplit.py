import sys
from fsplit.filesplit import FileSplit
from pathlib import Path

def write_func(outputs,filenames):
  for filename in filenames:
    fndir = filename.parent
    fndir.mkdir(parents=True,exist_ok=True)
  for output,filename in zip(outputs,filenames):
    with open(filename, 'w') as f:
      f.write(output.getvalue())
  for filename in filenames:
    dirname = filename.parent
    new_pth_cmpts = dirname.relative_to(self.basedir)
    outdir = self.basedir.joinpath(new_pth_cmpts)
    fs = FileSplit(file=filename, splitsize=1_100_000, output_dir=outdir)
    fs.split()

def main(filename):
  pth = Path(filename).resolve()
  assert pth.exists(), pth
  pth_dirname = pth.parent
  outdir = pth.joinpath(pth.stem)
  outdir_relative = outdir.relative_to(pth)
  outdir_relative.mkdir(parents=True,exist_ok=True)
  fs = FileSplit(file=pth, splitsize=1_100_000, output_dir=outdir_relative)
  fs.split()

if __name__ == "__main__":
  filename = sys.argv[1]
  print(filename)
  main(filename)

