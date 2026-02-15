# Line Sampler Server-Client

A thread-safe server-client system for sampling lines from large text files without replacement. Lines are loaded into a global cache and can be randomly sampled by multiple concurrent clients.

## Features

- **Thread-safe cache** with locks for concurrent access
- **Unix domain sockets** for fast local communication
- **Load()**: Append lines from text files to global cache
- **Sample()**: Randomly sample lines (removed from cache)
- **Concurrent client support** with threading
- **No external dependencies** - pure Python standard library

## Installation

```bash
git clone https://github.com/yourusername/line-sampler-server
cd line-sampler-server