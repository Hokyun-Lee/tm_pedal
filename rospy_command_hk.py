import rospy
from src.tocabi_mobile import TocabiMobile, CommandBase
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy


class RospyListener(CommandBase):
    def __init__(self):
        super().__init__()
        rospy.init_node('tm_listener', anonymous=True, disable_signals=True)
        # rospy.Subscriber("/cmd_vel", Twist, self.callback)
        rospy.Subscriber("joy", Joy, self.pedalcallback)
        # self.MAF_size = 10
        # self.MAF_r = [0]*self.MAF_size
        # self.MAF_l = [0]*self.MAF_size
        # self.MAF_y = [0]*self.MAF_size
        self.threshold = 0.3

    # def callback(self,data):
    #     self.command[0] = data.linear.x
    #     self.command[1] = data.linear.y
    #     self.command[2] = data.angular.z
    
    def pedalcallback(self, data):
        # input : data.axes[0~2]
        # output : self.command[0~2] = 0
        # for backward. using mode. (external button required)
        # mode = 0~1 (0:foward, 1:backward)
        self.pedal_r = data.axes[0]
        self.pedal_l = data.axes[1]
        self.pedal_y = data.axes[2]

        # # Buffer Moving Average Filter(MAF)
        # self.MAF_r.pop()
        # self.MAF_r.insert(0, self.pedal_r)
        # self.pedal_r = sum(self.MAF_r)/len(self.MAF_r)
        # self.MAF_l.pop()
        # self.MAF_l.insert(0, self.pedal_l)
        # self.pedal_l = sum(self.MAF_l)/len(self.MAF_l)
        # self.MAF_y.pop()
        # self.MAF_y.insert(0, self.pedal_y)
        # self.pedal_y = sum(self.MAF_y)/len(self.MAF_y)

        if self.pedal_r > 0 and self.pedal_l > 0:
            diff = self.pedal_r - self.pedal_l
            if diff > self.threshold:
                # Right Diagonal Foward
                self.command[0] = min(self.pedal_r, self.pedal_l)
                self.command[1] = -diff
                self.command[2] = self.pedal_y
            elif diff < -self.threshold:
                # Left Diagonal Foward
                self.command[0] = min(self.pedal_r, self.pedal_l)
                self.command[1] = diff
                self.command[2] = self.pedal_y
            else:
                # Foward
                self.command[0] = min(self.pedal_r, self.pedal_l)
                self.command[1] = 0
                self.command[2] = self.pedal_y
        elif self.pedal_r > 0:
            # Right
            self.command[0] = 0
            self.command[1] = -self.pedal_r
            self.command[2] = self.pedal_y
        elif self.pedal_l > 0:
            # LEFT
            self.command[0] = 0
            self.command[1] = self.pedal_l
            self.command[2] = self.pedal_y
            

if __name__ == "__main__":
    rl = RospyListener()
    print("pedal_l : ")
    print(rl.pedal_l)
    print("\npedal_r : ")
    print(rl.pedal_r)
    print("\npedal_y : ")
    print(rl.pedal_y)
    tm = TocabiMobile(rl)
    tm.connect()
    tm.run()