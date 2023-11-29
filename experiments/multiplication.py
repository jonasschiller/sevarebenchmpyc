from mpyc.runtime import mpc

async def main():
    m = len(mpc.parties)
    l = m.bit_length()
    i = mpc.pid

    await mpc.start()
    print('m    =', await mpc.output(mpc.sum(mpc.input(mpc.SecInt(l+1)(1)))))
    print('m**2 =', await mpc.output(mpc.sum(mpc.input(mpc.SecInt(2*l+1)(2*i+1)))))
    print('2**m =', await mpc.output(mpc.prod(mpc.input(mpc.SecInt(m+2)(2)))))
    print('m!   =', await mpc.output(mpc.prod(mpc.input(mpc.SecInt(int(m*(l-1.4)+3))(i+1)))))
    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())