# -*- coding: utf-8 -*-
"""Interactive educational breast imaging simulation. Run: streamlit run breast_cancer_physics_sim.py"""
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title='ما وراء الورم | الفيزياء وسرطان الثدي', page_icon='🎀', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.5rem}h1,h2,h3{direction:rtl;text-align:right}p,li{direction:rtl;text-align:right}.stAlert{direction:rtl}</style>''', unsafe_allow_html=True)
st.title('🎀 ما وراء الورم | رحلة الفيزياء في الكشف عن سرطان الثدي')
st.caption('محاكاة تعليمية مبسطة — لا تُستخدم للكشف الطبي أو التشخيص أو تقدير احتمالية السرطان')

stage_names=['١ | من الخلية إلى الكتلة','٢ | التصوير بالأشعة السينية','٣ | الموجات فوق الصوتية','٤ | الرنين المغناطيسي','٥ | تحدّي اكتشاف المنطقة المشتبه بها']
st.sidebar.header('لوحة التحكم')
stage=st.sidebar.radio('اختاري فقرة الطالبة',stage_names)
radius=st.sidebar.slider('نصف قطر الكتلة الافتراضية',5,27,14)
density=st.sidebar.slider('كثافة النسيج الغدي الافتراضية (%)',10,90,45)
contrast=st.sidebar.slider('قوة الاختلاف بين الأنسجة (%)',10,100,65)
show_mass=st.sidebar.checkbox('إظهار موضع الكتلة (للمقدمة)',False)

N=240
y,x=np.mgrid[-1:1:complex(N),-1:1:complex(N)]
body=((x/0.87)**2+(y/0.92)**2)<1
cx,cy=0.25,-0.14
r=radius/120
mass=((x-cx)**2+(y-cy)**2)<r*r
# Smooth deterministic heterogeneity, not patient data.
texture=(np.sin(10*x+3*y)*np.cos(9*y-2*x)+np.sin(19*x-8*y))/2
fibro=(np.sin(7*x+4*y)+np.cos(12*y-3*x)+np.sin(15*x+9*y))/3
background=np.clip(0.35+0.30*(density/100)+0.12*texture+0.12*fibro,0.05,0.9)


def display(arr,title,cmap='gray',vmin=None,vmax=None,marker=False):
    fig,ax=plt.subplots(figsize=(6.3,5.4),facecolor='#101622')
    ax.set_facecolor('#101622')
    img=np.where(body,arr,np.nan)
    ax.imshow(img,cmap=cmap,origin='lower',extent=[-1,1,-1,1],vmin=vmin,vmax=vmax)
    ax.contour(x,y,body.astype(float),levels=[0.5],colors=['#d1d5db'],linewidths=1)
    if marker:
        circ=plt.Circle((cx,cy),r,fill=False,color='#ff668e',linewidth=2,linestyle='--')
        ax.add_patch(circ)
        ax.annotate('ROI',xy=(cx+r,cy),xytext=(cx+0.28,cy+0.24),color='#ff9eb7',arrowprops={'arrowstyle':'->','color':'#ff9eb7'})
    ax.set_xticks([]);ax.set_yticks([])
    ax.set_title(title,color='white',fontsize=13)
    for s in ax.spines.values():s.set_visible(False)
    fig.tight_layout()
    st.pyplot(fig,clear_figure=True)
    plt.close(fig)

strength=contrast/100
st.info('🎙️ عند الانتقال بين المراحل، تتولى طالبة شرح التقنية وتغيير الإعدادات أمام الحضور.')

if nstage==stage_names[0]:
    st.header('الطالبة الأولى | كيف تبدأ كتلة غير طبيعية؟')
    growth=st.slider('مرحلة النمو الافتراضي',0,100,55)
    simulated_r=(0.03+growth/100*0.20)
    growing=((x-cx)**2+(y-cy)**2)<simulated_r**2
    arr=background+growing*0.42
    display(arr,'نمو كتلة افتراضية داخل نموذج نسيجي',cmap='magma',marker=show_mass)
    st.markdown('**تقول الطالبة:** «سرطان الثدي قد يبدأ عندما تنمو خلايا غير طبيعية بصورة غير منضبطة. لكن ليست كل كتلة سرطانية. فكيف نستطيع رؤية التغيرات داخل الجسم؟ هنا تبدأ مهمة الفيزياء».')
    st.caption('النمو هنا تمثيل بصري تعليمي، وليس نموذجًا بيولوجيًا لتطور السرطان أو سرعته.')

elif nstage==stage_names[1]:
    st.header('الطالبة الثانية | الماموغرام والأشعة السينية')
    mu=0.7+background*0.8+mass*(0.1+strength*0.55)
    thickness=st.slider('السماكة الافتراضية للنسيج (وحدات نموذجية)',0.5,3.0,1.4,0.1)
    I0=1.0
    transmitted=I0*np.exp(-mu*thickness)
    c1,c2=st.columns(2)
    with c1:display(mu,'معامل التوهين النسبي',cmap='viridis',marker=show_mass)
    with c2:display(transmitted,'شدة الأشعة النافذة I/I₀',cmap='gray',vmin=0,vmax=1,marker=show_mass)
    st.latex(r'I=I_0 e^{-\mu x}')
    st.markdown('**تقول الطالبة:** «تمر الأشعة السينية عبر الثدي، وتضعف شدتها بمقادير مختلفة بحسب خصائص الأنسجة وسماكتها. ومن هذه الاختلافات تتكوّن صورة الماموغرام التي قد تكشف تغيرات تستدعي الفحص».')
    st.caption('هذا نموذج توهين أحادي الطاقة مبسط، لا يحاكي نظام ماموغرام سريريًا أو جرعة الإشعاع.')

elif nstage==stage_names[2]:
    st.header('الطالبة الثالثة | الموجات فوق الصوتية')
    freq=st.slider('تردد الموجة التوضيحي',2,12,6)
    wavefront=np.sin(freq*15*(y+0.9))
    z=1+background*0.3+mass*(0.12+strength*0.6)
    # Simplified contrast-enhanced echo, not a beamformed clinical ultrasound.
    gy,gx=np.gradient(z)
    reflect=np.sqrt(gx**2+gy**2)
    reflect/=max(reflect.max(),1e-9)
    echo=np.clip(0.18+0.35*np.abs(texture)+reflect*0.75,0,1)
    c1,c2=st.columns(2)
    with c1:display(wavefront,'جبهات الموجات الصوتية التوضيحية',cmap='coolwarm',vmin=-1,vmax=1,marker=show_mass)
    with c2:display(echo,'خريطة انعكاس صوتي مبسطة',cmap='gray',vmin=0,vmax=1,marker=show_mass)
    st.latex(r'R=\left(\frac{Z_2-Z_1}{Z_2+Z_1}\right)^2')
    st.markdown('**تقول الطالبة:** «عندما تقابل الموجات الصوتية أنسجة مختلفة في الممانعة الصوتية، ينعكس جزء من طاقتها. تساعد الأصداء في تكوين صور تكشف صفات الكتل، لكنها لا تثبت وحدها إن كانت سرطانية».')
    st.caption('خريطة انعكاس اصطناعية وليست صورة سونار سريرية أو محاكاة كاملة لحزمة المسبار.')

elif nstage==stage_names[3]:
    st.header('الطالبة الرابعة | الرنين المغناطيسي MRI')
    t=st.slider('زمن الصدى TE الافتراضي (مللي ثانية)',10,100,35)
    pd=0.5+0.4*background+mass*(0.08+0.35*strength)
    T2=30+65*background+mass*(8+25*strength)
    signal=pd*np.exp(-t/T2)
    display(signal,'إشارة MRI افتراضية موزونة بزمن T₂',cmap='gray',marker=show_mass)
    st.latex(r'S(TE)\propto \rho\,e^{-TE/T_2}')
    st.markdown('**تقول الطالبة:** «يستخدم الرنين المغناطيسي مجالًا مغناطيسيًا ونبضات تردد راديوي، ويقيس إشارات مرتبطة بالبروتونات وخواص استرخائها. تختلف شدة الإشارة باختلاف الأنسجة وإعدادات التصوير».')
    st.caption('نموذج مبسط لتناقص إشارة T₂ فقط؛ لا يمثل صور MRI المعززة بالتباين أو قدرته التشخيصية.')

else:
    st.header('الطالبة الخامسة | تحدّي الجمهور')
    st.write('اسألي الجمهور: هل يمكن تحديد المنطقة التي تستدعي فحصًا إضافيًا؟')
    reveal=st.checkbox('اكشفي موضع المنطقة الافتراضية بعد تصويت الجمهور',False)
    mu=0.7+background*0.8+mass*(0.1+strength*0.55)
    xray=np.exp(-mu*1.4)
    z=1+background*0.3+mass*(0.12+strength*0.6)
    gy,gx=np.gradient(z)
    ref=np.hypot(gx,gy);ref/=max(ref.max(),1e-9)
    echo=np.clip(0.18+0.35*np.abs(texture)+ref*0.75,0,1)
    pd=0.5+0.4*background+mass*(0.08+0.35*strength)
    T2=30+65*background+mass*(8+25*strength)
    mri=pd*np.exp(-35/T2)
    c1,c2,c3=st.columns(3)
    with c1:display(xray,'X-ray',marker=reveal)
    with c2:display(echo,'Ultrasound',marker=reveal)
    with c3:display(mri,'MRI',marker=reveal)
    if reveal:
        st.success('هذه منطقة افتراضية محددة مسبقًا داخل النموذج. ظهور اختلاف في الصورة لا يساوي تشخيص سرطان الثدي.')
    st.markdown('**تقول الطالبة:** «الفيزياء تساعدنا على رؤية ما لا تراه العين، لكن قراءة الصور وتحديد الخطوة التالية مسؤولية المختصين. وقد تستلزم بعض النتائج أخذ خزعة لتأكيد التشخيص».')

st.divider()
st.warning('تنبيه طبي: المحاكاة لا تقيّم المرضى ولا تميز بين الأورام الحميدة والخبيثة. التصوير الحراري ليس بديلًا عن فحوص الكشف المعتمدة، وتختلف اختيارات الفحوص بحسب الحالة والتوصيات الطبية.')
st.caption('نادي العلوم الأساسية | الفيزياء × التوعية بسرطان الثدي | محاكاة تعليمية باستخدام Python وStreamlit')
