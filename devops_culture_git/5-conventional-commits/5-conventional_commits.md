# Conventional Commits

## Git log

```text
e4ba537 docs: add HolbieBot usage instructions
d01361e test: add energy validation tests
81402dd refactor: extract energy validation
2554bbe fix: clamp energy values
d17b4c5 feat: add deployment capability
```

## Commit type explanations

- `feat`: adds a new deployment capability to HolbieBot.
- `fix`: corrects invalid energy values by keeping them between 0 and 100.
- `refactor`: moves the energy validation into a dedicated function without changing the program's behavior.
- `test`: adds automated tests for the energy validation logic.
- `docs`: adds instructions explaining how to run HolbieBot and its tests.
