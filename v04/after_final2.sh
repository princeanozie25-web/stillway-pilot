#!/bin/bash
# after_final2.sh : waits for the final queue, the pilots and the exploratory run, then runs the idle-machine benchmarks.
until grep -q "final_all done" logs/v04_queue.log 2>/dev/null; do sleep 20; done
while pgrep -f "stillway4.arms" > /dev/null || pgrep -f "stillway4.reader" > /dev/null || pgrep -f "x_cont_10x" > /dev/null || pgrep -f "stillway4.scratchpad" > /dev/null; do sleep 20; done
./v04/final_bench.sh
