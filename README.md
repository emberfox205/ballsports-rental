# ballsports-rental

![Static Badge](https://img.shields.io/badge/Python-3.12.0-blue?style=flat&logo=Python&logoColor=white)

Computer Vision project to automate the dispense and retrieval of rental equipment for selected ball sports.

---

## Installation

### Repo preparation

Clone the repository via HTTPS:

```Bash
git clone https://github.com/emberfox205/ballsports-rental.git 
```

Alternatively, if you have SSH installed:

```Bash
git clone git@github.com:emberfox205/ballsports-rental.git
```

[Optional] Setup a virtual environment of your choice (e.g. venv, conda). Make sure the Python version is 3.12.0.

Install dependencies:

```Bash
pip install -r requirements.txt
```

In the file `check_database.json`, set `{"database_init": 0}`.

### Model installation

This repository only offers the web application interface for the ball classification and logo detection models.

To use the application, download the required models here: [ballsports-rental-ai](https://huggingface.co/emberfox205/ballsports-rental-ai)

In your local repo, setup a folder named `models`.

Move the 2 models into `models`.

Rename the ball classification model into `model.keras`.

Rename the logo detection model into `logo.keras`.

### HTTPS Certification

As the application utilizes the device's integrated webcam, you are required to generate an https certificate and key.

Use OpenSSL:

- Windows:
  - [Third-party releases](https://slproweb.com/products/Win32OpenSSL.html)
  - [Usage guide](https://www.progress.com/blogs/how-to-use-openssl-to-generate-certificates)
- Linux:
  - [Guide](https://docs.openiam.com/docs-4.2.1.3/appendix/2-openssl)

> [!note] For Windows users
> If you follow the usage guide for Windows, the key and certificate should be found in `C:\\Users\\USER`.
> `USER` may differ on your device.
>

Now you should have a certificate (`*.crt`) and private key (`*.key`).

In your local repo, setup a folder named `certs`.

Move the certificate and key into `certs`.

Rename the certificate into `certificate.crt`.

Rename the key into `private.key`.

## Running the program

While in the local repo, enter into the terminal:

```Bash
python dashboard.py
```

Follow either of the addresses following Flask's warning in the terminal.

Upon browser's warning, click 'Advanced', then 'Continue/Proceed to ...'.

Allow for Camera permission if asked.
