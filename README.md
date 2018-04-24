# nix2go

Dropping tools into an arbitrary environment can be a pain.
Many tools' build systems were not designed with static compilation in mind, and other tools require non-binary runtime files (e.g. Python or nmap) anyways.
Ensuring all of the necessary libraries and other runtime dependencies in nonstandard locations can be found in the environmnet is no fun at all.
Nix provides an elegant solution to these problems.

This repository contains the files necessary to prepare a Nix closure to run somewhere other than the Nix store by substituting Nix store paths in Nix outputs using a user-supplied Python function.

For example, given the following closure:

```
/nix/store/84h2zni7h805k0i1ys2bba3dsp1cqnhh-glibc-2.26-131
/nix/store/4d4h3iryz4lm2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
/nix/store/q1g0rl8zfmz7r371fp5p42p4acmv297d-bash-4.4-p19
/nix/store/7y4vpnf777743j2ln309qg7i4vivflz5-libpcap-1.8.1
/nix/store/qc84dvliy1dzpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
/nix/store/0m6i66q8lf3rnlvqhxfak0ddrm8s50hy-nmap-7.70
/nix/store/5bwa088n5wmh2glssyqc4anin8jqzqzm-tzdata-2017c
/nix/store/7dk9vv9ns2sp8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
/nix/store/9npbzymd6lagkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2
/nix/store/b36lm9ark178zm3aqr6py7jvjirabai7-libmnl-1.0.4
/nix/store/fsmv83b29z7yji4h9g5ap6x90sdjr4wj-iana-etc-20180108
/nix/store/hj8ccijzngiragn6ljw49rvdaj3lh8ci-libnfnetlink-1.0.1
/nix/store/pwrykr9g779y14lqxzc28lgx825qvx88-libnetfilter_queue-1.0.3
/nix/store/pksk16jg2jkp2kv2v16k26ahvx0d7f6n-bettercap-2.4-bin
/nix/store/xswwka30pm521sm8c2npiqha6rxr4nxa-entry.sh
```
`nix2go.bundle` creates the following bundle of directories, each containing patched binaries, with no dependencies on the Nix store:
```
/tmp/nothingtoseehere/5k0i1ys2bba3dsp1cqnhh-glibc-2.26-131
/tmp/nothingtoseehere/m2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
/tmp/nothingtoseehere/7r371fp5p42p4acmv297d-bash-4.4-p19
/tmp/nothingtoseehere/43j2ln309qg7i4vivflz5-libpcap-1.8.1
/tmp/nothingtoseehere/zpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
/tmp/nothingtoseehere/rnlvqhxfak0ddrm8s50hy-nmap-7.70
/tmp/nothingtoseehere/h2glssyqc4anin8jqzqzm-tzdata-2017c
/tmp/nothingtoseehere/p8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
/tmp/nothingtoseehere/gkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2
/tmp/nothingtoseehere/8zm3aqr6py7jvjirabai7-libmnl-1.0.4
/tmp/nothingtoseehere/yji4h9g5ap6x90sdjr4wj-iana-etc-20180108
/tmp/nothingtoseehere/ragn6ljw49rvdaj3lh8ci-libnfnetlink-1.0.1
/tmp/nothingtoseehere/y14lqxzc28lgx825qvx88-libnetfilter_queue-1.0.3
/tmp/nothingtoseehere/p2kv2v16k26ahvx0d7f6n-bettercap-2.4-bin
/tmp/nothingtoseehere/21sm8c2npiqha6rxr4nxa-entry.sh
```

## Simple Example

```
>>> cat example.nix
with import <nixpkgs> {};

let

  nix2go = callPackages ./. {};

in rec {

  entry = nix2go.setup "${busybox}/bin/ash" [ busybox nmap tcpdump bettercap ];

  bundle = nix2go.bundle {
    rootPaths = [ entry ];
    script = ./example.py;
    excludes = [ "/man/" "/doc/" ];
  };

}

>>> cat example.py
def f(x):
    prefix = '/tmp/nothingtoseehere/'
    return prefix + x[len(prefix):]

>>> entry=$(nix-build example.nix -A entry)

>>> nix-store -qR $entry
/nix/store/84h2zni7h805k0i1ys2bba3dsp1cqnhh-glibc-2.26-131
/nix/store/4d4h3iryz4lm2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
/nix/store/q1g0rl8zfmz7r371fp5p42p4acmv297d-bash-4.4-p19
/nix/store/7y4vpnf777743j2ln309qg7i4vivflz5-libpcap-1.8.1
/nix/store/qc84dvliy1dzpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
/nix/store/0m6i66q8lf3rnlvqhxfak0ddrm8s50hy-nmap-7.70
/nix/store/5bwa088n5wmh2glssyqc4anin8jqzqzm-tzdata-2017c
/nix/store/7dk9vv9ns2sp8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
/nix/store/9npbzymd6lagkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2
/nix/store/b36lm9ark178zm3aqr6py7jvjirabai7-libmnl-1.0.4
/nix/store/fsmv83b29z7yji4h9g5ap6x90sdjr4wj-iana-etc-20180108
/nix/store/hj8ccijzngiragn6ljw49rvdaj3lh8ci-libnfnetlink-1.0.1
/nix/store/pwrykr9g779y14lqxzc28lgx825qvx88-libnetfilter_queue-1.0.3
/nix/store/pksk16jg2jkp2kv2v16k26ahvx0d7f6n-bettercap-2.4-bin
/nix/store/xswwka30pm521sm8c2npiqha6rxr4nxa-entry.sh

>>> bundle=$(nix-build example.nix -A bundle)

>>> echo $bundle
/nix/store/7q59cm4w9l3v6qx94clb62pf49rrlc4p-nix2go-bundle

>>> ls $bundle/tmp/nothingtoseehere/
21sm8c2npiqha6rxr4nxa-entry.sh
43j2ln309qg7i4vivflz5-libpcap-1.8.1
5k0i1ys2bba3dsp1cqnhh-glibc-2.26-131
7r371fp5p42p4acmv297d-bash-4.4-p19
8zm3aqr6py7jvjirabai7-libmnl-1.0.4
gkk5cvk8f2wqa2v5ingwl-tcpdump-4.9.2
h2glssyqc4anin8jqzqzm-tzdata-2017c
m2vsg58bx0qfyr11nq5sx-openssl-1.0.2o
p2kv2v16k26ahvx0d7f6n-bettercap-2.4-bin
p8r1xhwwf3ahj9k2yg1a9-busybox-1.28.1
ragn6ljw49rvdaj3lh8ci-libnfnetlink-1.0.1
rnlvqhxfak0ddrm8s50hy-nmap-7.70
y14lqxzc28lgx825qvx88-libnetfilter_queue-1.0.3
yji4h9g5ap6x90sdjr4wj-iana-etc-20180108
zpidw10yvpi3di5f0q4vj-gcc-7.3.0-lib
```

Move the contents of `$bundle` to another environment.
Perhaps a server or device in a network you wish to explore...

Now execute `/tmp/nothingtoseehere/21sm8c2npiqha6rxr4nxa-entry.sh` on that server or device, and voila:
```
>>> which nmap
/tmp/nothingtoseehere/rnlvqhxfak0ddrm8s50hy-nmap-7.70/bin/nmap
>>> nmap -v -A scanme.nmap.org
Starting Nmap 7.70 ( https://nmap.org ) at 2018-04-23 04:31 UTC
...
```

## Another Example

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
