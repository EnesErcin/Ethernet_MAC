#include <stdio.h>
#include <inttypes.h>
// Assumes little endian
void printBits(size_t const size, void const * const ptr)
{
    unsigned char *b = (unsigned char*) ptr;
    unsigned char byte;
    int i, j;
    
    for (i = size-1; i >= 0; i--) {
        for (j = 7; j >= 0; j--) {
            byte = (b[i] >> j) & 1;
            printf("%u", byte);
        }
    }
    printf("\t num_bit: %lu", sizeof(size)*8);
    puts("");
}

unsigned char reverse_byte(unsigned char b)
{
	unsigned char	r = 0;
	unsigned		byte_len = 8;

	while (byte_len--)
	{
		r = (r << 1) | (b & 1);
		b >>= 1;
	}
	return (r);
}


uint32_t reverse(uint32_t b)
{
	uint32_t	r = 0;
    printf("The reversed messeage : \t %x \n",b);
    printBits(sizeof(uint32_t),&b);
	int	byte_len = 32;

	while (byte_len--)
	{
		r = (r << 1) | (b & 1);
		b >>= 1;
	}
    printf("The reversed messeage : \t %x \n",r);
    printBits(sizeof(uint32_t),&r);
	return (r);
}


int main(void){

    unsigned char k =  'a';
    uint32_t myInt = 0xABCD1234;

    reverse(myInt);

    return 0;
}