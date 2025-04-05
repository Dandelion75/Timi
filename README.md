# Timi
progress bar to show time spent in year and much more

A terminal app to visualize time progess in form of progress bar.

---

## 📦 Installation

### From GitHub

```bash
pip install git+https://github.com/Dandelion75/timi.git
```

## From Source

Clone the repository and install the built wheel from `dist/`:

```bash
git clone https://github.com/your-username/timi.git
cd timi
python -m build
pip install dist/timi-1.0.0-py3-none-any.whl
```

---

## 🛠 Usage

After installation, launch the app with:

```bash
timi --help
```

To run the app:

```bash
timi
```

### Options

- Adjust refresh rate using the `--interval` flag:

  ```bash
  timi --interval 0.1
  ```

- Control which time progress bar to display using the `--show` flag (in singular) :

  ```bash
  timi --show min hour day month
  ```

---

## Inspiration

There are many videos which are like  "25% of your year is over" but there wasnt any cli for that so I wrote one with a progress bar. 

This project was heavily inspired by [sampler](https://github.com/sqshq/sampler?tab=readme-ov-file#gauge) as I wasn't able to get it working on my windows machine

## Contributing

This is my first project so there might be some issues and bugs so any issues and PR are appreciated! You can do that by

- Open an issue if you have any bug or feature request
- Open a Pull Request if you have any feature

or just fix a typo --__--

## 📃 License

Licensed under the **GPL-3.0-or-later**. See [LICENSE](./LICENSE) for details.

