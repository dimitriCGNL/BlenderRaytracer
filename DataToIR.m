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
%H(:,1) = highpass(H(:,1),150,fs);
F =linspace(0, 1, length(H(:,2)))*1E-10;
for i=1:length(H(:,2))
    C(i)=H(i,2)+F(i);
end
G=linspace(min(H(:,2)),max(H(:,2)),max(H(:,2))*44100);
B=interp1(C,H(:,1),G);
Z=[B;G];
Z=Z';
fs2=round(length(Z)/max(Z(:,2)));
Z(:,1)=highpass(Z(:,1),200,fs2);
Z(:,1)=lowpass(Z(:,1),22000,fs2);
A = Z(:,1)./(max(abs(Z(:,1))));
plot(Z(:,2),A)
audiowrite("testIR.wav",A,fs2);
[x,FS]=audioread("Dry signal.wav");
[y]=fconv(x,A);
random = rand(1, length(y));
for i=1:length(y)
YNoisy(i) = y(i) + (5*10^-3) * random(i);
end
YNoisy = YNoisy(:)./(max(abs(YNoisy(:))));
audiowrite('conv.wav',YNoisy,FS);
RT=t60(A,fs2,0);
RT=RT/1000;


%{
f = fs2*(0:(length(A)/2))/length(A);
a=fft(A);
P2 = abs(a/length(A));
P1 = P2(1:length(A)/2+1);
P1(2:end-1) = 2*P1(2:end-1);
plot(f,P1);
%}