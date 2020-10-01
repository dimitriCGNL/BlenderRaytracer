clearvars
close all
clc
%%
D = readmatrix("D.txt");
D=D(~isnan(D));
L = readmatrix("L.txt");
L=L(~isnan(L));
%%
h=[L;D];
H=h';
H=sortrows(H,2);
fs=round(length(H)/max(H(:,2)));
H(:,1) = lowpass(H(:,1),50,fs);
F =linspace(0, 1, length(H(:,2)))*1E-10;
for i=1:length(H(:,2))
    C(i)=H(i,2)+F(i);
end
G=linspace(min(H(:,2)),max(H(:,2)),max(H(:,2))*fs);
B=interp1(C,H(:,1),G);
Z=[B;G];
Z=Z';
A = Z(:,1)./(max(abs(Z(:,1))));
plot(Z(:,2),A)
audiowrite("testIR.wav",A,fs);
[x,FS]=audioread("Dry signal.wav");
[y]=fconv(x,A);
audiowrite('conv.wav',y,FS);