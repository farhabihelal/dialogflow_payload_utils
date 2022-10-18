# Haru Smalltalk Utils

This repo provides some added control and utility to the Smalltalk Demo.


## Setup

After cloning this repo, run the `post_clone.sh` from the root directory of this repo.

```
cd /path/to/this/repo/
chmod +x post_clone.sh
./post_clone.sh
```

## Usage

### ROS 

Build the `catkin_ws`.
```
cd /path/to/catkin/ws/
ln -s /path/to/this/repo/ .
catkin_make
```

Launch using `roslaunch`.

```
roslaunch haru_smalltalk_utils haru_smalltalk_utils.launch
```


### Standalone

```
python3 src/main.py
```