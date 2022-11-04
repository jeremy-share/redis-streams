# Redis Streams Example

Example of Redis Streams

Shared in the hope it is useful to someone

## Running
```shell
make up-core
echo "Wait for a while and make sure everything starts"
make up-publisher-consumer
echo "Ctrl+c to exit when ready"
make logs-publisher-consumer
make stop
```

## Links / References
* https://huogerac.hashnode.dev/using-redis-stream-with-python
