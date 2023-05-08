import numpy as np
import matplotlib.pyplot as plt



save_dir = './'


TRecNet_hist = np.load('TRecNet/TRecNet_6jets_20230411_161458/TRecNet_6jets_20230411_161458_TrainHistory.npy',allow_pickle=True).item()
TRecNet_hist2 = np.load('TRecNet/TRecNet_6jets_20230419_123850/TRecNet_6jets_20230419_123850_TrainHistory.npy',allow_pickle=True).item()

TRecNet_ttbar_hist = np.load('TRecNet+ttbar/TRecNet+ttbar_6jets_20230411_234414/TRecNet+ttbar_6jets_20230411_234414_TrainHistory.npy',allow_pickle=True).item()
TRecNet_ttbar_hist2 = np.load('TRecNet+ttbar/TRecNet+ttbar_6jets_20230419_174504/TRecNet+ttbar_6jets_20230419_174504_TrainHistory.npy',allow_pickle=True).item()

JetPretrainer_hist = np.load('JetPretrainer/JetPretrainer_6jets_20230412_144558/JetPretrainer_6jets_20230412_144558_TrainHistory.npy',allow_pickle=True).item()

TRecNet_ttbar_JetPretrain_hist = np.load('TRecNet+ttbar+JetPretrain/TRecNet+ttbar+JetPretrain_6jets_20230413_193930/TRecNet+ttbar+JetPretrain_6jets_20230413_193930_TrainHistory.npy',allow_pickle=True).item()
TRecNet_Unfrozen_hist = np.load('TRecNet+ttbar+JetPretrainUnfrozen/TRecNet+ttbar+JetPretrain_6jets_20230413_193930/TRecNet+ttbar+JetPretrain_6jets_20230413_193930_TrainHistory.npy',allow_pickle=True).item()
TRecNet_ttbar_JetPretrain_hist2 = np.load('TRecNet+ttbar+JetPretrain/TRecNet+ttbar+JetPretrain_6jets_20230418_135607/TRecNet+ttbar+JetPretrain_6jets_20230418_135607_TrainHistory.npy',allow_pickle=True).item()
TRecNet_Unfrozen_hist2 = np.load('TRecNet+ttbar+JetPretrainUnfrozen/TRecNet+ttbar+JetPretrainUnfrozen_6jets_20230418_175519/TRecNet+ttbar+JetPretrainUnfrozen_6jets_20230418_175519_TrainHistory.npy',allow_pickle=True).item()

last_epoch = len(TRecNet_ttbar_JetPretrain_hist['loss'])
new_epochs = [last_epoch + epoch for epoch in range(len(TRecNet_Unfrozen_hist['loss']))]

last_epoch2 = len(TRecNet_ttbar_JetPretrain_hist2['loss'])
new_epochs2 = [last_epoch2 + epoch for epoch in range(len(TRecNet_Unfrozen_hist2['loss']))]



# MAE Plot
plt.figure()
plt.plot(TRecNet_hist['loss'], label='TRN Train', color="tab:orange", alpha=0.7)
plt.plot(TRecNet_hist['val_loss'], '--',label='TRN Val', color="tab:orange", alpha=0.7)
plt.plot(TRecNet_hist2['loss'], label='TRN Train 2', color="tab:orange")
plt.plot(TRecNet_hist2['val_loss'], '--',label='TRN Val 2', color="tab:orange")
plt.plot(TRecNet_ttbar_hist['loss'], label='TRN+ttbar Train', color="tab:pink", alpha=0.7)
plt.plot(TRecNet_ttbar_hist['val_loss'], '--',label='TRN+ttbar Val', color="tab:pink", alpha=0.7)
plt.plot(TRecNet_ttbar_hist2['loss'], label='TRN+ttbar Train 2', color="tab:pink")
plt.plot(TRecNet_ttbar_hist2['val_loss'], '--',label='TRN+ttbar Val 2', color="tab:pink")
#plt.plot(TRecNet_ttbar_JetPretrain_hist['loss'], label='TRN+ttbar+JP Train', color="tab:purple")
#plt.plot(TRecNet_ttbar_JetPretrain_hist['val_loss'], '--',label='TRN+ttbar+JP Val', color="tab:purple")
#plt.plot(new_epochs, TRecNet_Unfrozen_hist['loss'], label='Finetuning Train', color="tab:purple", alpha=0.6)
#plt.plot(new_epochs, TRecNet_Unfrozen_hist['val_loss'], '--',label='Finetuning Val', color="tab:purple", alpha=0.6)
plt.plot(TRecNet_ttbar_JetPretrain_hist2['loss'], label='TRN+ttbar+JP Train 2', color="tab:purple")
plt.plot(TRecNet_ttbar_JetPretrain_hist2['val_loss'], '--',label='TRN+ttbar+JP Val 2', color="tab:purple")
plt.plot(new_epochs2, TRecNet_Unfrozen_hist2['loss'], label='Finetuning Train 2', color="tab:purple", alpha=0.6)
plt.plot(new_epochs2, TRecNet_Unfrozen_hist2['val_loss'], '--',label='Finetuning Val 2', color="tab:purple", alpha=0.6)
plt.xlabel('Epoch')
plt.ylabel('MAE')
plt.legend()
plt.title('MAE Loss')
plt.savefig(save_dir+'MAE_Loss',bbox_inches='tight')


# MSE Plot
plt.figure()
plt.plot(TRecNet_hist['mse'], label='TRN Train', color="tab:orange")
plt.plot(TRecNet_hist['val_mse'], '--',label='TRN Val', color="tab:orange")
plt.plot(TRecNet_ttbar_hist['mse'], label='TRN+ttbar Train', color="tab:pink")
plt.plot(TRecNet_ttbar_hist['val_mse'], '--',label='TRN+ttbar Val', color="tab:pink")
#plt.plot(TRecNet_ttbar_JetPretrain_hist['mse'], label='TRN+ttbar Train', color="tab:purple")
#plt.plot(TRecNet_ttbar_JetPretrain_hist['val_mse'], '--',label='TRN+ttbar+JP Val', color="tab:purple")
#plt.plot(new_epochs, TRecNet_Unfrozen_hist['mse'], label='Finetuning Train', color="tab:purple", alpha=0.6)
#plt.plot(new_epochs, TRecNet_Unfrozen_hist['val_mse'], '--',label='Finetuning Val', color="tab:purple", alpha=0.6)
plt.plot(TRecNet_ttbar_JetPretrain_hist2['mse'], label='TRN+ttbar Train 2', color="tab:purple")
plt.plot(TRecNet_ttbar_JetPretrain_hist2['val_mse'], '--',label='TRN+ttbar+JP Val 2', color="tab:purple")
plt.plot(new_epochs2, TRecNet_Unfrozen_hist2['mse'], label='Finetuning Train 2', color="tab:purple", alpha=0.6)
plt.plot(new_epochs2, TRecNet_Unfrozen_hist2['val_mse'], '--',label='Finetuning Val 2', color="tab:purple", alpha=0.6)
plt.xlabel('Epoch')
plt.ylabel('MSE')
plt.legend()
plt.title('MSE Loss')
plt.savefig(save_dir+'MSE_Loss',bbox_inches='tight')


# Binary Cross-Entropy Plot
plt.figure()
plt.plot(JetPretrainer_hist['loss'],label='Train',color="tab:purple")
plt.plot(JetPretrainer_hist['val_loss'], '--', label='Val',color="tab:purple")
plt.xlabel('Epoch')
plt.ylabel('Binary Cross Entropy')
plt.legend()
plt.title('Binary Cross Entropy Loss')
plt.savefig(save_dir+'/BinaryCrossEntropy_Loss',bbox_inches='tight')