# freegpus

As an alternative to running `nvidia-smi`, this utility will print the indices of unused GPUs.

Basic usage:

```shell
> freegpus
4 5 # Indices of unused GPUs
```

```shell
> freegpus -r
5 4 # Indices of unused GPUs ordered randomly, so that if you take first index you won't always take the same
```

```shell
> freegpus -w # Get usernames of people using GPUs
alice 1,7
bob 0,2,3
carol 6
```
