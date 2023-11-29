import pickle
from mpyc.runtime import mpc


async def main():
    # Load the array
    with open('Data/Input.txt', 'r') as file:
        array = eval(file.read())

    # Securely multiply the arrays using mpyc
    await mpc.start()
    secureArray = mpc.SecureArray()
    array_enc = mpc.input(secureArray(array))
    result_enc = mpc.mul(array_enc)
    result = mpc.output(result_enc)
    await mpc.shutdown()
    print(result)
if __name__ == '__main__':
    mpc.run(main())