#!/usr/bin/env python

from __future__ import print_function
import argparse
import signal
import sys
import time

import rtmidi
import sysv_ipc
import math

KEY = 81

class DetectedObject():

    def __init__(self):
        self.label_name = ""
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0


def parse_receive_data(receive_str):
    ret_array = []

    arr = receive_str.split(";")
    
    d = None
    i = 0
    num = 5

    screen_w = int(arr[0])
    screen_h = int(arr[1])

    del arr[:2]

    for a in arr:
        if i%num == 0:
            d = DetectedObject()
            d.label_name = a
        elif i%num == 1:
            d.left = int(a)
        elif i%num == 2:
            d.top = int(a)
        elif i%num == 3:
            d.right = int(a)
        elif i%num == 4:
            d.bottom = int(a)
            ret_array.append(d)
        i += 1


    return (ret_array, screen_w, screen_h )




def signal_handler(signal, frame):
    """Handler for Ctrl-C"""
    sys.exit(0)


def midi_in_callback(value, args):
    data = value[0]
    if args['hex']:
        print('[' + ', '.join('0x%02X' % x for x in data) + ']')
    else:
        print(data)

def midi_send(device_id, data_array):
    outport = rtmidi.MidiOut()
    if not device_id < len(outport.get_ports()):
        raise Exception('Device id out of range')
    outport.open_port(device_id)
    '''
    if args['hex']:
        data = [int(x, 16) for x in args['write']]
    else:
        data = [int(x, 0) for x in args['write']]
    '''
    outport.send_message(data_array)
    del outport


'''
'''
def get_midi_cc(max_point, point, margin, cc_min = 0, cc_max = 127 ):
    
    if point <= margin:
        return cc_max
    if point >= (max_point - margin):
        return cc_min

    mp = max_point - margin*2
    p = point - margin

    return int(round( (cc_max-cc_min)*(1.0-float(p)/float(mp)) + cc_min))

def get_midi_note(max_point, point, margin, midi_note_array ):

    if point <= margin:
        return midi_note_array[0]
    if point >= (max_point - margin):
        return midi_note_array[ len(midi_note_array)-1 ]

    mp = max_point - margin*2
    p = point - margin
    one_note_width = mp / len(midi_note_array)
    index = int(math.floor(p/one_note_width))

    return midi_note_array[index]



def midi_send_server(args):
    # Write command, send data
    if not args['device']:
        raise Exception('No device specified')
    device_id = int(args['device'])
    outport = rtmidi.MidiOut()
    if not device_id < len(outport.get_ports()):
        raise Exception('Device id out of range')
    outport.open_port(device_id)
    if args['hex']:
        data = [int(x, 16) for x in args['write']]
    else:
        data = [int(x, 0) for x in args['write']]
    outport.send_message(data)
    del outport


if __name__ == '__main__':
    # Setup command line parser
    parser = argparse.ArgumentParser(description='MIDI tool')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List connected devices')
    parser.add_argument('-d', '--device', metavar='ID',
                        help='Select device')
    parser.add_argument('-w', '--write', type=str, nargs='+', metavar='DATA',
                        help='Write data')
    parser.add_argument('-r', '--read', action='store_true',
                        help='Read data')
    parser.add_argument('-x', '--hex', action='store_true',
                        help='Show/interprete data as hex')
    print(parser.parse_args())
    args = vars(parser.parse_args())

    try:

        if args['list']:
            # List command, show all connected devices
            print()
            print('Available ports:')
            print()
            print('\tInput:')
            print('\t', 'ID', 'Name', sep='\t')
            for i, name in enumerate(rtmidi.MidiIn().get_ports()):
                print('\t', i, name, sep='\t')
            print()
            print('\tOutput:')
            print('\t', 'ID', 'Name', sep='\t')
            for i, name in enumerate(rtmidi.MidiOut().get_ports()):
                print('\t', i, name, sep='\t')
            print()

        elif args['write']:
            #midi_send_server(args)
            #midi_send( 0, [0x90, 80, 100])
            #midi_send( 1, [128, 80, 100])
            print("KEY:", KEY)
            mq = sysv_ipc.MessageQueue(KEY)
            print("id:", mq.id)
            print("ready to receive messages.")
            #device_id = int(args['device'])

            MIDI_ID = 1
            CC_NO = 20
            OBJECT_1ST = "banana"
            OBJECT_2ND = "apple"
            OBJECT_3RD = "orange"
            #OBJECT_4TH = "frisbee"

            OBJECT_1ST_DOWN_MIDI_NOTE = 0
            OBJECT_1ST_UP_MIDI_NOTE = 0

            SCREEN_MARGIN = 60

            NOISE_VOLUME = 0


            while True:
                mtext, mtype = mq.receive(type=1)
                #print(mtext.decode("utf-8"))
                ret, screen_w, screen_h = parse_receive_data(mtext.decode("utf-8"))
                #print("SCREEN_WIDTH:", screen_w)
                #print("SCREEN_HEIGHT:", screen_h)

                # Send MIDI UP NOTE 
                if OBJECT_1ST_DOWN_MIDI_NOTE != 0 and OBJECT_1ST_UP_MIDI_NOTE == 0:
                    midi_send( MIDI_ID, [0x80, OBJECT_1ST_DOWN_MIDI_NOTE, 100])
                    OBJECT_1ST_UP_MIDI_NOTE = OBJECT_1ST_DOWN_MIDI_NOTE 

                find_2nd_object = False

                for r in ret:
                    print(r.label_name)
                    center_x = (r.left + r.right)/2
                    center_y = (r.top + r.bottom)/2
                    #center_x = r.left
                    #center_y = r.top

                    if r.label_name == OBJECT_1ST:
                        # X Position is assigned MIDI NOTE.
                        '''
                        MAIN_MIDI_ARRAY = [108, 109, 110, 111, 112, 113, 114, 115]
                        one_note_width = screen_w / len(MAIN_MIDI_ARRAY)
                        index = math.floor(center_x/one_note_width)
                        midi_note = MAIN_MIDI_ARRAY[index]
						'''
                        midi_note = get_midi_note(screen_w, center_x, SCREEN_MARGIN, [108, 109, 110, 111, 112, 113, 114, 115])

                        if OBJECT_1ST_DOWN_MIDI_NOTE != midi_note:
                            midi_send( MIDI_ID, [0x90, midi_note, 100])
                            OBJECT_1ST_DOWN_MIDI_NOTE = midi_note
                            OBJECT_1ST_UP_MIDI_NOTE = 0 
                            print("down midi:" + str(midi_note) + " " + OBJECT_1ST)
                        else:
                            print("no push midi." +  OBJECT_1ST)

                        # Y Position is assigned CC MIDI 20
                        CC_NO = 20
                        CC_DATA = get_midi_cc(screen_h, center_y, SCREEN_MARGIN)
                        print("CC_DATA:" + str(CC_DATA))
                        midi_send( MIDI_ID, [185, CC_NO, CC_DATA])

                    elif r.label_name == OBJECT_2ND:
                        find_2nd_object = True
                    	# X Position is assigned CC MIDI 21 -> Analog Freq
                        CC_NO = 21
                        CC_DATA = get_midi_cc(screen_w, center_x, SCREEN_MARGIN)
                        midi_send( MIDI_ID, [185, CC_NO, CC_DATA])

                    	# Y Position is assigned CC MIDI 22
                        CC_NO = 22
                        midi_send( MIDI_ID, [185, CC_NO, get_midi_cc(screen_h, center_y, SCREEN_MARGIN)])

                    elif r.label_name == OBJECT_3RD:

                    	# Y Position is assigned CC MIDI 25
                        CC_NO = 25
                        midi_send( MIDI_ID, [185, CC_NO, get_midi_cc(screen_h, center_y, SCREEN_MARGIN)])

                    	# X Position is assigned CC MIDI 26
                        CC_NO = 27
                        midi_send( MIDI_ID, [185, CC_NO, get_midi_cc(screen_w, center_x, SCREEN_MARGIN)])

                    '''
                    elif r.label_name == OBJECT_4TH:

                    	# Y Position is assigned CC MIDI 24
                        CC_NO = 24
                        midi_send( MIDI_ID, [185, CC_NO, get_midi_cc(screen_h, center_y, SCREEN_MARGIN)])

                    	# X Position is assigned CC MIDI 26
                        CC_NO = 26
                        midi_send( MIDI_ID, [185, CC_NO, get_midi_cc(screen_w, center_x, SCREEN_MARGIN)])
					'''

                # NOISE CHANNEL VOLUME
                if find_2nd_object == True:
                	NOISE_VOLUME += 2
                	if NOISE_VOLUME > 127:
                		NOISE_VOLUME = 127
                else:
                	NOISE_VOLUME -= 2
                	if NOISE_VOLUME < 0:
                		NOISE_VOLUME = 0

                CC_NO = 23
                midi_send( MIDI_ID, [185, CC_NO, NOISE_VOLUME])



                time.sleep(0.016)

            # Write command, send data
            '''
            if not args['device']:
                raise Exception('No device specified')
            device_id = int(args['device'])
            outport = rtmidi.MidiOut()
            if not device_id < len(outport.get_ports()):
                raise Exception('Device id out of range')
            outport.open_port(device_id)
            if args['hex']:
                data = [int(x, 16) for x in args['write']]
            else:
                data = [int(x, 0) for x in args['write']]
            outport.send_message(data)
            del outport
            '''

        elif args['read']:
            # Read command, receive data until Ctrl-C is pressed
            signal.signal(signal.SIGINT, signal_handler)
            if not args['device']:
                raise Exception('No device specified')
            device_id = int(args['device'])
            inport = rtmidi.MidiIn()
            if not device_id < len(inport.get_ports()):
                raise Exception('Device id out of range')
            inport.open_port(device_id)
            inport.set_callback(midi_in_callback, args)
            inport.ignore_types(False, False, False)
            while True:
                time.sleep(1)

    except Exception as e:
        print('Error:', e)
