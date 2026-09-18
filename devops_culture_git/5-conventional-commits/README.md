# HolbieBot

HolbieBot is a small Python program used to demonstrate Conventional Commits.

It can:

- report its current energy level;
- keep energy values between 0 and 100;
- start a deployment.

## Run the program

```bash
python3 devops_bot.py
```

Expected output:

```text
HolbieBot is online with 100% energy
Deployment started
```

## Run the tests

```bash
python3 -m unittest
```

The test suite checks that:

- a normal energy value such as `50` stays unchanged;
- a value below `0` becomes `0`;
- a value above `100` becomes `100`.
