# Fadecandy Manager

This is for running animations on a Raspberry Pi Zero with a 
[Adafruit 128x64 OLED Bonnet for Raspberry Pi](https://www.adafruit.com/product/3531)
and a [FadeCandy](https://www.adafruit.com/product/1689) attached.

### /etc/rc.local
```
/usr/local/bin/fcserver /usr/local/bin/fcserver.json >/var/log/fcserver.log 2>&1 &

python3 /home/pi/dasblinkencloud/control.py > /var/log/control.log 2>&1 &
```

