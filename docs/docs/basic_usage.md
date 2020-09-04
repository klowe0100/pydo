---
title: Basic Usage
date: 20200301
author: Lyz
---

All you need to know to use `pydo` effectively are these four commands (`add`, `do`, `del`,
`open`).

# Add

To add a task run:

```bash
pydo add Improve the pydo manual
```

It is also possible to immediately add tags or projects when creating a task:

```bash
pydo add Improve the pydo manual pro:task_management +python
```

# Open

To see the open tasks run:

```bash
pydo open
```

By default, `open` is the default command, so you can execute `pydo` alone.

# Do

If you've completed a task, run:

```bash
pydo do {{ task_filter }}
```

Where `{{ task_filter }}`  can be a task id extracted from the `open` report or
a task expression like `pro:task_management +python`.

# Delete

If you no longer need a task, run:

```bash
pydo del {{ task_filter }}
```

If you are new to `pydo`, it is recommended that you stop here, go and start to
manage your task list for a while. We don't want you to be overwhelmed at a time
when you just need a way to organize and get things done.

When you are comfortable with basic `pydo` usage, there are many other features
you can learn about. While you are not expected to learn all of them, or even
find them useful, you might just find exactly what you need.
