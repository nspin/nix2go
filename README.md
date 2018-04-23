# nix2go

Prepare a Nix closure to run somewhere other than the Nix store.

For example, given the following closure:

```
/nix/store/0m6i66q8lf3rnlvqhxfak0ddrm8s50hy-nmap-7.70
/nix/store/4d4h3iryz4lm2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
/nix/store/7dk9vv9ns2sp8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
/nix/store/7y4vpnf777743j2ln309qg7i4vivflz5-libpcap-1.8.1
/nix/store/84h2zni7h805k0i1ys2bba3dsp1cqnhh-glibc-2.26-131
/nix/store/9npbzymd6lagkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2
/nix/store/gcnx2pb3c5sgywzgvysws4y2lx7w99qq-entry.sh
/nix/store/ggb7k5x9855j10dz99467djx4rplg32b-perl-5.24.3
/nix/store/hr386dzm459zc9q82ylwcgwci7jqwzfz-acl-2.2.52
/nix/store/q1g0rl8zfmz7r371fp5p42p4acmv297d-bash-4.4-p19
/nix/store/qc84dvliy1dzpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
/nix/store/qrxs7sabhqcr3j9ai0j0cp58zfnny0jz-coreutils-8.29
```
create the following bundle of directories with no dependencies on the Nix store:
```
/tmp/nothingtoseehere/rnlvqhxfak0ddrm8s50hy-nmap-7.70
/tmp/nothingtoseehere/m2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
/tmp/nothingtoseehere/p8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
/tmp/nothingtoseehere/43j2ln309qg7i4vivflz5-libpcap-1.8.1
/tmp/nothingtoseehere/5k0i1ys2bba3dsp1cqnhh-glibc-2.26-131
/tmp/nothingtoseehere/gkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2
/tmp/nothingtoseehere/gywzgvysws4y2lx7w99qq-entry.sh
/tmp/nothingtoseehere/j10dz99467djx4rplg32b-perl-5.24.3
/tmp/nothingtoseehere/zc9q82ylwcgwci7jqwzfz-acl-2.2.52
/tmp/nothingtoseehere/7r371fp5p42p4acmv297d-bash-4.4-p19
/tmp/nothingtoseehere/zpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
/tmp/nothingtoseehere/r3j9ai0j0cp58zfnny0jz-coreutils-8.29
```

It works by substituting Nix store paths in Nix outputs using a user-supplied Python function.

## Example

```
>>> # build "empty" image (you can't actually run "scratch")
>>> docker build -t empty .

>>> # test environment without building it
>>> ./test-pre-bundle.sh $(nix-build ./example.nix -A entry)
/ # which nmap
/nix/store/0m6i66q8lf3rnlvqhxfak0ddrm8s50hy-nmap-7.70/bin/nmap
/ # nmap -v -A scanme.nmap.org
Starting Nmap 7.70 ( https://nmap.org ) at 2018-04-23 04:31 UTC
...
Nmap done: 1 IP address (1 host up) scanned in 31.26 seconds
           Raw packets sent: 1400 (72.534KB) | Rcvd: 1330 (60.504KB)

>>> # test actual environment
>>> bundle=$(nix-build example.nix -A bundle)
>>> entry="$(find $bundle -name '*-entry.sh' | sed s,$bundle,,)"
>>> ./test-bundle.sh /tmp/nothingtoseehere $bundle "$entry"
/ # which nmap
/tmp/nothingtoseehere/rnlvqhxfak0ddrm8s50hy-nmap-7.70/bin/nmap
/ # ls /tmp/nothingtoseehere
43j2ln309qg7i4vivflz5-libpcap-1.8.1         m2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
5k0i1ys2bba3dsp1cqnhh-glibc-2.26-131        p8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
7cvrsqa3s307rqy7rrckn-cowsay-3.03+dfsg1-16  r3j9ai0j0cp58zfnny0jz-coreutils-8.29
7r371fp5p42p4acmv297d-bash-4.4-p19          rnlvqhxfak0ddrm8s50hy-nmap-7.70
gkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2         z4qpgcbqhvavnbdnf8k6c-attr-2.4.47
gywzgvysws4y2lx7w99qq-entry.sh              zc9q82ylwcgwci7jqwzfz-acl-2.2.52
j10dz99467djx4rplg32b-perl-5.24.3           zpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
/ # nmap -v -A scanme.nmap.org | cowsay
 _________________________________________
/ Starting Nmap 7.70 ( https://nmap.org ) \
| at 2018-04-23 04:49 UTC NSE: Loaded 148 |
| scripts for scanning. NSE: Script       |
| Pre-scanning. Initiating NSE at 04:49   |

...

| TRACEROUTE (using port 80/tcp) HOP RTT  |
| ADDRESS 1 0.04 ms 172.17.0.1 2 0.27 ms  |
| 10.0.2.2 3 0.71 ms scanme.nmap.org      |
| (45.33.32.156)                          |
|                                         |
| NSE: Script Post-scanning. Initiating   |
| NSE at 04:51 Completed NSE at 04:51,    |
| 0.00s elapsed Initiating NSE at 04:51   |
| Completed NSE at 04:51, 0.00s elapsed   |
| Read data files from:                   |
| /tmp/nothingtoseehere/rnlvqhxfak0ddrm8s |
| 50hy-nmap-7.70/bin/../share/nmap OS and |
| Service detection performed. Please     |
| report any incorrect results at         |
| https://nmap.org/submit/ . Nmap done: 1 |
| IP address (1 host up) scanned in 33.33 |
| seconds                                 |
|                                         |
| Raw packets sent: 1479 (74.258KB) |     |
\ Rcvd: 1406 (61.910KB)                   /
 -----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```
