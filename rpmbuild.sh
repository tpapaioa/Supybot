#!/bin/bash

cp ~/git/Supybot/supybot.spec ~/rpmbuild/SPECS/
mkdir /tmp/supybot-0.83.4.2
cp -ar ~/git/Supybot/* /tmp/supybot-0.83.4.2/
tar -C /tmp -czf ~/rpmbuild/SOURCES/supybot-0.83.4.2.tar.gz supybot-0.83.4.2/
rm -rf /tmp/supybot-0.83.4.2/
rpmbuild -ba ~/rpmbuild/SPECS/supybot.spec
