#!/bin/bash
# Installation script

# Colors (tput)
# setaf - text/foreground color
# setab - background of the text color
txtcyn=$(tput setaf 6) # Cyan
txtgrn=$(tput setaf 2) # Green
txtred=$(tput setaf 1) # Red
txtrst=$(tput sgr0)    # Resets color

if [[ $EUID -ne 0 ]]; then
	echo "${txtred}## This script must be run as root user! ##${txtrst}" 1>&2
	exit 1
fi

echo "${txtcyn}Installing required packages...${txtrst}"

success=0
apt-get update

## Python

python=$(dpkg-query -W -f='${status}' python3 | grep -c 'ok installed')

if [ $python -eq 0 ]; then
	echo "${txtcyn}=== Installing Python... ===${txtrst}"
	add-apt-repository ppa:deadsnakes/ppa
	apt-get update 2>&1 >/dev/null
	apt-get install -y python3 2>&1 >/dev/null
	python3 --version
	
	control1=$(dpkg-query -W -f='${status}' python3 | grep -c 'ok installed')
	
	if [ $control1 -eq 1 ]; then
		let "success++"
	fi
else
	echo "${txtcyn}=== Python 3 is already installed ===${txtrst}"
	python3 --version
	let "success++"
fi

## pip - for installing / updating modules

pip=$(dpkg-query -W -f='${status}' python3-pip | grep -c 'ok installed')

if [ $pip -eq 0 ]; then
	echo "${txtcyn}=== Installing pip3... ===${txtrst}"
	apt-get install -y python3-pip 2>&1 >/dev/null
	pip3 --version
	
	control2=$(dpkg-query -W -f='${status}' python3-pip | grep -c 'ok installed')
	
	if [ $control2 -eq 1 ]; then
		let "success++"
	fi
else
	echo "${txtcyn}=== pip is already installed ===${txtrst}"
	pip3 --version
	let "success++"
fi

## FluidSynth - for converting MIDI files into WAV type

fluidsynth=$(dpkg-query -W -f='${status}' fluidsynth | grep -c 'ok installed')

if [ $fluidsynth -eq 0 ]; then
	echo "${txtcyn}=== Installing FluidSynth... ===${txtrst}"
	apt-get install -y fluidsynth 2>&1 >/dev/null
	fluidsynth --version

	control3=$(dpkg-query -W -f='${status}' fluidsynth | grep -c 'ok installed')

	if [ $control3 -eq 1 ]; then
		let "success++"
	fi
else
	echo "${txtcyn}=== FluidSynth is already installed ===${txtrst}"
	fluidsynth --version
	let "success++"
fi

## ffmpeg - codec for to play in voice channel

ffmpeg=$(dpkg-query -W -f='${status}' ffmpeg | grep -c 'ok installed')

if [ $ffmpeg -eq 0 ]; then
	echo "${txtcyn}=== Installing ffmpeg... ===${txtrst}"
	apt-get install -y ffmpeg 2>&1 >/dev/null
	ffmpeg --version

	control4=$(dpkg-query -W -f='${status}' ffmpeg | grep -c 'ok installed')

	if [ $control4 -eq 1 ]; then
		let "success++"
	fi
else
	echo "${txtcyn}=== ffmpeg is already installed ===${txtrst}"
	fluidsynth --version
	let "success++"
fi

## End result and final touches

if [ $success -eq 4 ]; then
	echo "${txtgrn}=== Packages are successfully installed ===${txtrst}"
	echo "${txtcyn}=== chmod +x start.sh ===${txtrst}"
	chmod +x start.sh
	
	echo "${txtcyn}=== Making rc.local file... ===${txtrst}" # for starting up whenever machine boots up
	echo "#!/bin/sh -e" > /etc/rc.local
	echo "# rc.local" >> /etc/rc.local
	echo "" >> /etc/rc.local
	echo "cd $PWD && sh start.sh" >> /etc/rc.local
	echo "" >> /etc/rc.local
	echo "exit 0" >> /etc/rc.local
	
	chown root /etc/rc.local
	chmod +x /etc/rc.local
	
	echo "${txtgrn}=== All done! Exiting the script... ===${txtrst}"
elif [ $success -lt 4 ]; then
	echo "${txtred}=== Some packages are not installed, please try again ===${txtrst}"
fi

exit 0