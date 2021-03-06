git pull
./source_sync.sh
docker-compose down
docker-compose build

# Build the base Nvidia Cuda
cd ComposeMediaKrakenNvidia
#docker build -t mediakraken/mkbasenvidia .

cd ../ComposeMediaKrakenNvidiaDebian
docker build -t mediakraken/mkbasenvidiadebian .

# Build the base FFMPEG from base images
cd ../ComposeMediaKrakenBaseFFMPEG
docker build -t mediakraken/mkbaseffmpeg .

#cd ../ComposeMediaKrakenBaseFFMPEGNvidia
#docker build -t mediakraken/mkbaseffmpegnvidia .

cd ../ComposeMediaKrakenBaseFFMPEGNvidiaDebian
docker build -t mediakraken/mkbaseffmpegnvidiadebian .

# Build the base slave images from other base images
cd ../ComposeMediaKrakenSlave
docker build -t mediakraken/mkslave .

#cd ../ComposeMediaKrakenSlaveNvidia
#docker build -t mediakraken/mkslavenvidia .

cd ../ComposeMediaKrakenSlaveNvidiaDebian
docker build -t mediakraken/mkslavenvidiadebian .


