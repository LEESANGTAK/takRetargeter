import takRetargeter as takRT
reload(takRT)

srcCd = takRT.charDefinition.CharDefinition()
srcCd.pelvis = 'Bip001'
srcCd.spine_01 = 'Bip001_Spine'
srcCd.spine_02 = 'Bip001_Spine1'
srcCd.spine_03 = 'Bip001_Spine2'
srcCd.neck_01 = 'Bip001_Neck'
srcCd.head = 'Bip001_Head'

srcCd.clavicle_l = 'Bip001_L_Clavicle'
srcCd.upperarm_l = 'Bip001_L_UpperArm'
srcCd.lowerarm_l = 'Bip001_L_Forearm'
srcCd.hand_l = 'Bip001_L_Hand'

srcCd.index_01_l = 'Bip001_L_Finger1'
srcCd.index_02_l = 'Bip001_L_Finger11'
srcCd.index_03_l = 'Bip001_L_Finger12'
srcCd.middle_01_l = 'Bip001_L_Finger2'
srcCd.middle_02_l = 'Bip001_L_Finger21'
srcCd.middle_03_l = 'Bip001_L_Finger22'
srcCd.ring_01_l = 'Bip001_L_Finger3'
srcCd.ring_02_l = 'Bip001_L_Finger31'
srcCd.ring_03_l = 'Bip001_L_Finger32'
srcCd.pinky_01_l = 'Bip001_L_Finger4'
srcCd.pinky_02_l = 'Bip001_L_Finger41'
srcCd.pinky_03_l = 'Bip001_L_Finger42'
srcCd.thumb_01_l = 'Bip001_L_Finger0'
srcCd.thumb_02_l = 'Bip001_L_Finger01'
srcCd.thumb_03_l = 'Bip001_L_Finger02'

srcCd.clavicle_r = 'Bip001_R_Clavicle'
srcCd.upperarm_r = 'Bip001_R_UpperArm'
srcCd.lowerarm_r = 'Bip001_R_Forearm'
srcCd.hand_r = 'Bip001_R_Hand'

srcCd.index_01_r = 'Bip001_R_Finger1'
srcCd.index_02_r = 'Bip001_R_Finger11'
srcCd.index_03_r = 'Bip001_R_Finger12'
srcCd.middle_01_r = 'Bip001_R_Finger2'
srcCd.middle_02_r = 'Bip001_R_Finger21'
srcCd.middle_03_r = 'Bip001_R_Finger22'
srcCd.ring_01_r = 'Bip001_R_Finger3'
srcCd.ring_02_r = 'Bip001_R_Finger31'
srcCd.ring_03_r = 'Bip001_R_Finger32'
srcCd.pinky_01_r = 'Bip001_R_Finger4'
srcCd.pinky_02_r = 'Bip001_R_Finger41'
srcCd.pinky_03_r = 'Bip001_R_Finger42'
srcCd.thumb_01_r = 'Bip001_R_Finger0'
srcCd.thumb_02_r = 'Bip001_R_Finger01'
srcCd.thumb_03_r = 'Bip001_R_Finger02'

srcCd.thigh_l = 'Bip001_L_Thigh'
srcCd.calf_l = 'Bip001_L_Calf'
srcCd.foot_l = 'Bip001_L_Foot'
srcCd.ball_l = 'Bip001_L_Toe0'

srcCd.thigh_r = 'Bip001_R_Thigh'
srcCd.calf_r = 'Bip001_R_Calf'
srcCd.foot_r = 'Bip001_R_Foot'
srcCd.ball_r = 'Bip001_R_Toe0'

srcCdFilePath = r'C:\Users\chst27\Desktop\Bip.cd'
srcCd.save(srcCdFilePath)
srcCd.load(srcCdFilePath)
srcCd.setPose()


trgCd = takRT.charDefinition.CharDefinition()
trgCd.pelvis = 'Castanic_F_rig:RootX_M'
trgCd.spine_01 = 'Castanic_F_rig:FKSpine1_M'
trgCd.spine_02 = 'Castanic_F_rig:FKSpine2_M'
trgCd.spine_03 = 'Castanic_F_rig:FKChest_M'
trgCd.neck_01 = 'Castanic_F_rig:FKNeck_M'
trgCd.head = 'Castanic_F_rig:FKHead_M'

trgCd.clavicle_l = 'Castanic_F_rig:FKScapula_L'
trgCd.upperarm_l = 'Castanic_F_rig:FKShoulder_L'
trgCd.lowerarm_l = 'Castanic_F_rig:FKElbow_L'
trgCd.hand_l = 'Castanic_F_rig:FKWrist_L'

trgCd.index_01_l = 'Castanic_F_rig:FKIndexFinger1_L'
trgCd.index_02_l = 'Castanic_F_rig:FKIndexFinger2_L'
trgCd.index_03_l = 'Castanic_F_rig:FKIndexFinger3_L'
trgCd.middle_01_l = 'Castanic_F_rig:FKMiddleFinger1_L'
trgCd.middle_02_l = 'Castanic_F_rig:FKMiddleFinger2_L'
trgCd.middle_03_l = 'Castanic_F_rig:FKMiddleFinger3_L'
trgCd.ring_01_l = 'Castanic_F_rig:FKRingFinger1_L'
trgCd.ring_02_l = 'Castanic_F_rig:FKRingFinger2_L'
trgCd.ring_03_l = 'Castanic_F_rig:FKRingFinger3_L'
trgCd.pinky_01_l = 'Castanic_F_rig:FKPinkyFinger1_L'
trgCd.pinky_02_l = 'Castanic_F_rig:FKPinkyFinger2_L'
trgCd.pinky_03_l = 'Castanic_F_rig:FKPinkyFinger3_L'
trgCd.thumb_01_l = 'Castanic_F_rig:FKThumbFinger1_L'
trgCd.thumb_02_l = 'Castanic_F_rig:FKThumbFinger2_L'
trgCd.thumb_03_l = 'Castanic_F_rig:FKThumbFinger3_L'

trgCd.clavicle_r = 'Castanic_F_rig:FKScapula_R'
trgCd.upperarm_r = 'Castanic_F_rig:FKShoulder_R'
trgCd.lowerarm_r = 'Castanic_F_rig:FKElbow_R'
trgCd.hand_r = 'Castanic_F_rig:FKWrist_R'

trgCd.index_01_r = 'Castanic_F_rig:FKIndexFinger1_R'
trgCd.index_02_r = 'Castanic_F_rig:FKIndexFinger2_R'
trgCd.index_03_r = 'Castanic_F_rig:FKIndexFinger3_R'
trgCd.middle_01_r = 'Castanic_F_rig:FKMiddleFinger1_R'
trgCd.middle_02_r = 'Castanic_F_rig:FKMiddleFinger2_R'
trgCd.middle_03_r = 'Castanic_F_rig:FKMiddleFinger3_R'
trgCd.ring_01_r = 'Castanic_F_rig:FKRingFinger1_R'
trgCd.ring_02_r = 'Castanic_F_rig:FKRingFinger2_R'
trgCd.ring_03_r = 'Castanic_F_rig:FKRingFinger3_R'
trgCd.pinky_01_r = 'Castanic_F_rig:FKPinkyFinger1_R'
trgCd.pinky_02_r = 'Castanic_F_rig:FKPinkyFinger2_R'
trgCd.pinky_03_r = 'Castanic_F_rig:FKPinkyFinger3_R'
trgCd.thumb_01_r = 'Castanic_F_rig:FKThumbFinger1_R'
trgCd.thumb_02_r = 'Castanic_F_rig:FKThumbFinger2_R'
trgCd.thumb_03_r = 'Castanic_F_rig:FKThumbFinger3_R'

trgCd.thigh_l = 'Castanic_F_rig:FKHip_L'
trgCd.calf_l = 'Castanic_F_rig:FKKnee_L'
trgCd.foot_l = 'Castanic_F_rig:FKAnkle_L'
trgCd.ball_l = 'Castanic_F_rig:FKToes_L'

trgCd.thigh_r = 'Castanic_F_rig:FKHip_R'
trgCd.calf_r = 'Castanic_F_rig:FKKnee_R'
trgCd.foot_r = 'Castanic_F_rig:FKAnkle_R'
trgCd.ball_r = 'Castanic_F_rig:FKToes_R'

trgCdFilePath = r'C:\Users\chst27\Desktop\Castanic_F.cd'
trgCd.save(trgCdFilePath)
trgCd.load(trgCdFilePath)
trgCd.setPose()


rt = takRT.retargeter.Retargeter()
rt.targetCharDef = trgCd
rt.sourceCharDef = srcCd
rt.connect()



import takRetargeter as takRT
reload(takRT)

srcCd = takRT.charDefinition.CharDefinition()
srcCdFilePath = r'C:\Users\chst27\Desktop\Bip.cd'
srcCd.load(srcCdFilePath)

trgCd = takRT.charDefinition.CharDefinition()
trgCdFilePath = r'C:\Users\chst27\Desktop\Castanic_F.cd'
trgCd.load(trgCdFilePath)

rt = takRT.retargeter.Retargeter()
rt.targetCharDef = trgCd
rt.sourceCharDef = srcCd
rt.connect()