from LiberalOverflow.models import Lecture, TimeSlot
dow = [('Monday', 'Wednesday'), ('Tuesday', 'Thursday')]
days = ['Monday', 'Wednesday', 'Tuesday', 'Thursday', 'Friday']
time_pair = [(9.0, 10.5), (10.5, 12.0), (13.0, 14.5), (14.5, 16.0), (16.0, 17.5)]
lecture_names = ['법과 사회생활', '경제와 법', '사회학개론', 'Intermediate English Speaking & Listening', '스페인어 회화', '불어 회화', '현대 중국의 이해', '논리학과 인공지능', '경제학개론', '한국문학특강<조선선비의 생활과 정신>']
professor_names = ['배덕현', '배덕현', '윤정로', '레드펀', '유왕무', '윤현', '이승욱', '박우석', '장두석', '김광년']

for day in days:
    for t in time_pair:
        TimeSlot(day_of_week=day, start_time=t[0], end_time=t[1]).save()

for i in range(len(dow)):
    for j in range(len(time_pair)):
        lec = Lecture()
        lec.lecture_name = lecture_names[5*i+j]
        lec.professor_name = professor_names[5*i+j]
        lec.save()
        print(dow[i][0])
        print(time_pair[j][0])
        print(time_pair[j][1])
        lec.time_slots.add(TimeSlot.objects.get(day_of_week=dow[i][0], start_time=time_pair[j][0], end_time=time_pair[j][1]))
        print(dow[i][1])
        print(time_pair[j][0])
        print(time_pair[j][1])
        lec.time_slots.add(TimeSlot.objects.get(day_of_week=dow[i][1], start_time=time_pair[j][0], end_time=time_pair[j][1]))
        lec.save()

lec = Lecture()
lec.lecture_name = '사회과학특강<국제분쟁과 미디어>'
lec.professor_name = '강경란'
lec.save()
lec.time_slots.add(TimeSlot.objects.get(day_of_week='Friday', start_time=9.0, end_time=10.5))
lec.time_slots.add(TimeSlot.objects.get(day_of_week='Friday', start_time=10.5, end_time=12.0))
lec.save()
lec = Lecture()
lec.lecture_name = '배드민턴'
lec.professor_name = 'Staff'
lec.save()
lec.time_slots.add(TimeSlot.objects.get(day_of_week='Friday', start_time=13.0, end_time=14.5))
lec.save()



