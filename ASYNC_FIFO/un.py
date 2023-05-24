from threading import Thread, Event
from time import sleep
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles

import cocotb
from cocotb.queue import Queue, QueueFull
from cocotb.triggers import RisingEdge, Timer, First, Event

def task(event, id,holdesc):
    print(f'Thread {id} started. Waiting for the signal....')
    event.wait()
    print("Initated {}".format(id))
    sleep(holdesc)
    print(f'Received signal. The thread {id} was completed.')

class tb:
    def __init__(self,dut):
        self.dequeue_event = Event()
        self.clock = dut.clk

async def send(self, frame):
    while self.full():
        self.dequeue_event.clear()
        await self.dequeue_event.wait()


async def _run(self):
    frame = None
    frame_offset = 0
    frame_data = None
    frame_error = None
    ifg_cnt = 0
    self.active = False

    clock_edge_event = RisingEdge(self.clock)

    enable_event = None
    if self.enable is not None:
        enable_event = RisingEdge(self.enable)

    while True:
        await clock_edge_event

        if self.enable is None or self.enable.value:
            if ifg_cnt > 0:
                # in IFG
                ifg_cnt -= 1

            elif frame is None and not self.queue.empty():
                # send frame
                frame = self.queue.get_nowait()
                self.dequeue_event.set()


def main():
    my_class =tb()


    print('Blocking the main thread for 3 seconds...')
    sleep(1) 
    event.set()



if __name__ == '__main__':
    main()