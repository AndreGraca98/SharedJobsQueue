
# Rename tools
cp run_client.py JobsClient
cp run_server.py JobsServer

# Create executable
chmod +x JobsClient
chmod +x JobsServer

# Create bin and copy tools to bin
mkdir -p ~/bin
cp -r jobs_queue ~/bin
cp JobsClient ~/bin
cp JobsServer ~/bin

source ~/.profile
