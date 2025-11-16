# MY CCWC TOOL
A simple linux tool that micmics the `wc` command.

## Features
* `-w` - word count 
* `-l` - line count
* `-c` - file/stream byte size
* `-m` - character count

## Installation
- Clone repo
```bash
git clone https://github.com/Tha-Orakkle/ccwc
cd ccwc
```

- Activate a virtual environment
```bash
virtualenv venv
source venv/bin/activate # Linux/MacOS
.\venv\Scripts\activate.bat # Windows
```

- Install `ccwc`
```bash
pip install -e .
```

Once installation is complete, the tool is ready to use.

## Usage
```bash
ccwc <file>
```
* `ccwc` can be used with nultiple files at a go.
```bash
ccwc <file1> <file2> <file3>
```
* `ccwc` can also read from standard input (stdin):
```bash
cat <file> | ccwc
```
* For help, run the command with `--help` or `-h` flag:
```bash
ccwc --help
# OR
ccwc -h
```
* To use specific features, use the respective flags:
```bash
ccwc -w <file>  # word count
ccwc -l <file>  # line count
ccwc -c <file>  # byte size
ccwc -m <file>  # character count
```

* If no flags are provided, all counts will be displayed by default:
```bash
ccwc <file>  # displays line, word and byte size
```
## License


## Author
Paul Adegbiran-Ayinoluwa (Tha-Orakkle)
- GitHub: [Tha-Orakkle](https://github.com/Tha-Orakkle)
- Email: adegbiranayinoluwa.paul@yahoo.com