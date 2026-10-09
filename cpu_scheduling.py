
import copy  # นำเข้าโมดูล copy เพื่อใช้ deepcopy (คัดลอกข้อมูลแบบไม่ผูกกับต้นฉบับ)
 
 
def print_gantt_chart(gantt_blocks):  # ฟังก์ชันวาด Gantt Chart รับ list ของช่วงเวลาที่แต่ละ process ทำงาน
    """ฟังก์ชันสำหรับแสดงผล Gantt Chart"""
    if not gantt_blocks:  # ถ้า list ว่าง (ไม่มีอะไรให้วาด)
        return  # ออกจากฟังก์ชันทันที
 
    print("\n--- Gantt Chart ---")  # พิมพ์หัวข้อ Gantt Chart (ขึ้นบรรทัดใหม่ก่อน 1 บรรทัด)
 
    # บรรทัดบน (กล่องแสดงชื่อ Process และ Idle)
    top_line = ""  # สร้าง string ว่างไว้สะสมบรรทัดบนของกราฟ
    for b in gantt_blocks:  # วนทีละช่วงเวลา (block)
        p_name = b["process"]  # ดึงชื่อ process ของ block นี้ เช่น "P1" หรือ "Idle"
        duration = b["end"] - b["start"]  # คำนวณระยะเวลาที่ทำงาน = เวลาจบ - เวลาเริ่ม
        width = max(len(p_name), duration * 2, 4)  # ความกว้างกล่อง = ค่าที่มากสุดของ ความยาวชื่อ, duration*2, และ 4
        top_line += f"| {p_name.center(width-2)} "  # ต่อกล่อง: ขีด | แล้วชื่อ process จัดกึ่งกลางในกล่อง
    top_line += "|"  # ปิดท้ายบรรทัดด้วยขีด | ตัวสุดท้าย
    print(top_line)  # พิมพ์บรรทัดบนออกหน้าจอ
 
    # บรรทัดล่าง (แสดงช่วงเวลา Time Scale)
    time_line = f"{gantt_blocks[0]['start']}"  # เริ่มบรรทัดล่างด้วยเวลาเริ่มของ block แรก
    for b in gantt_blocks:  # วนทีละ block อีกรอบ
        duration = b["end"] - b["start"]  # คำนวณระยะเวลาของ block (สูตรเดียวกับข้างบน)
        width = max(len(b["process"]), duration * 2, 4)  # คำนวณความกว้างกล่อง (ต้องเท่ากับข้างบนเพื่อให้ตัวเลขตรงกล่อง)
        time_line += f"{str(b['end']).rjust(width + 2)}"  # ต่อเวลาจบของ block โดยชิดขวาในช่องกว้าง width+2
    print(time_line)  # พิมพ์บรรทัดเวลาออกหน้าจอ
    print("-" * 65)  # พิมพ์เส้นขีดยาว 65 ตัวคั่น
 
 
def simulate_fcfs(processes):  # ฟังก์ชันจำลอง FCFS (มาก่อนได้ก่อน)
  # ป้องกันข้อมูลต้นฉบับเสียหายด้วย deepcopy
  procs = copy.deepcopy(processes)  # คัดลอก process ทั้งหมดมาใช้ เพื่อไม่ให้แก้ข้อมูลต้นฉบับ
  procs = sorted(procs, key=lambda x: (x["at"], x["id"]))  # เรียงตาม Arrival Time ก่อน ถ้าเท่ากันเรียงตาม id
  time = 0  # เวลาปัจจุบันของ CPU เริ่มที่ 0
  results = []  # list เก็บผลลัพธ์ของแต่ละ process
  gantt_blocks = []  # list เก็บช่วงเวลาสำหรับวาด Gantt Chart
 
  for p in procs:  # วนทีละ process ตามลำดับที่เรียงไว้
    if time < p["at"]:  # ถ้าเวลาปัจจุบันยังน้อยกว่าเวลาที่ process มาถึง (CPU ว่าง)
      # กรณี CPU ว่าง (Idle)
      gantt_blocks.append({"process": "Idle", "start": time, "end": p["at"]})  # บันทึกช่วงที่ CPU ว่าง
      time = p["at"]  # ข้ามเวลาไปถึงตอนที่ process มาถึง
 
    start = time  # เวลาเริ่มทำงานของ process นี้
    ct = start + p["bt"]  # Completion Time = เวลาเริ่ม + Burst Time
    time = ct  # อัปเดตเวลาปัจจุบันเป็นเวลาที่ทำเสร็จ
 
    gantt_blocks.append({"process": p["id"], "start": start, "end": ct})  # บันทึกช่วงเวลาทำงานลง Gantt
 
    tat = ct - p["at"]  # Turnaround Time = เวลาเสร็จ - เวลามาถึง
    wt = tat - p["bt"]  # Waiting Time = Turnaround Time - Burst Time
 
    results.append({  # เพิ่มผลลัพธ์ของ process นี้เข้า list
        "id": p["id"],  # ชื่อ process
        "at": p["at"],  # Arrival Time
        "bt": p["bt"],  # Burst Time
        "ct": ct,  # Completion Time
        "tat": tat,  # Turnaround Time
        "wt": wt,  # Waiting Time
    })  # ปิด dictionary และปิดการ append
 
  avg_tat = sum(r["tat"] for r in results) / len(results)  # ค่าเฉลี่ย TAT = ผลรวม TAT / จำนวน process
  avg_wt = sum(r["wt"] for r in results) / len(results)  # ค่าเฉลี่ย WT = ผลรวม WT / จำนวน process
 
  return results, avg_tat, avg_wt, gantt_blocks  # ส่งผลลัพธ์ ค่าเฉลี่ย และข้อมูล Gantt กลับไป
 
 
def simulate_sjf(processes):  # ฟังก์ชันจำลอง SJF แบบ non-preemptive (งานสั้นสุดก่อน)
  procs = [  # สร้าง list process ใหม่พร้อมฟิลด์เพิ่ม
      dict(p, remaining=p["bt"], completed=False)  # ก๊อป dict เดิม แล้วเพิ่ม remaining และ completed
      for p in copy.deepcopy(processes)  # วนจากสำเนาของ process ต้นฉบับ
  ]  # ปิด list comprehension
 
  time = 0  # เวลาปัจจุบันเริ่มที่ 0
  completed = 0  # นับจำนวน process ที่ทำเสร็จแล้ว
  n = len(procs)  # จำนวน process ทั้งหมด
  results = {}  # dict เก็บผลลัพธ์ โดยใช้ id เป็น key
  gantt_blocks = []  # list เก็บข้อมูลวาด Gantt Chart
 
  while completed < n:  # วนจนกว่าทุก process จะเสร็จ
    available = [p for p in procs if not p["completed"] and p["at"] <= time]  # หา process ที่ยังไม่เสร็จและมาถึงแล้ว
 
    if not available:  # ถ้าไม่มี process พร้อมทำงานเลย
      # หา AT ถัดไปที่ใกล้ที่สุดเพื่อข้ามเวลาไป
      next_at = min(p["at"] for p in procs if not p["completed"])  # หาเวลามาถึงที่น้อยสุดของ process ที่ยังไม่เสร็จ
      gantt_blocks.append({"process": "Idle", "start": time, "end": next_at})  # บันทึกช่วง CPU ว่าง
      time = next_at  # ข้ามเวลาไปถึงตอนที่มี process มา
      continue  # กลับไปต้นลูป while เพื่อเช็คใหม่
 
    # เลือก Process ที่ Burst Time น้อยที่สุด (ถ้าเท่ากันเทียบ AT และ ID)
    p = min(available, key=lambda x: (x["bt"], x["at"], x["id"]))  # เลือกตัวที่ BT น้อยสุด (เสมอกันดู AT แล้วดู id)
 
    start = time  # เวลาเริ่มทำงานของ process ที่เลือก
    ct = start + p["bt"]  # เวลาเสร็จ = เวลาเริ่ม + Burst Time
    time = ct  # อัปเดตเวลาปัจจุบัน
 
    p["completed"] = True  # ทำเครื่องหมายว่า process นี้เสร็จแล้ว
    completed += 1  # เพิ่มตัวนับจำนวนที่เสร็จแล้ว
 
    gantt_blocks.append({"process": p["id"], "start": start, "end": ct})  # บันทึกช่วงเวลาทำงานลง Gantt
 
    tat = ct - p["at"]  # Turnaround Time = เวลาเสร็จ - เวลามาถึง
    wt = tat - p["bt"]  # Waiting Time = TAT - Burst Time
 
    results[p["id"]] = {  # เก็บผลลัพธ์ลง dict โดยใช้ id เป็น key
        "id": p["id"],  # ชื่อ process
        "at": p["at"],  # Arrival Time
        "bt": p["bt"],  # Burst Time
        "ct": ct,  # Completion Time
        "tat": tat,  # Turnaround Time
        "wt": wt,  # Waiting Time
    }  # ปิด dictionary
 
  res_list = [  # แปลงผลลัพธ์จาก dict เป็น list เรียงตาม id
      results[p["id"]]  # ดึงผลลัพธ์ของ process ตาม id
      for p in sorted(copy.deepcopy(processes), key=lambda x: x["id"])  # วนตามลำดับ id ที่เรียงแล้ว
  ]  # ปิด list comprehension
 
  avg_tat = sum(r["tat"] for r in res_list) / n  # ค่าเฉลี่ย Turnaround Time
  avg_wt = sum(r["wt"] for r in res_list) / n  # ค่าเฉลี่ย Waiting Time
 
  return res_list, avg_tat, avg_wt, gantt_blocks  # ส่งผลลัพธ์กลับไป
 
 
def simulate_rr_exact(processes, quantum):  # ฟังก์ชันจำลอง Round Robin รับ process และ time quantum
  procs = [  # สร้าง list process ใหม่สำหรับใช้จำลอง
      {  # เริ่ม dictionary ของแต่ละ process
          "id": p["id"],  # ชื่อ process
          "at": p["at"],  # Arrival Time
          "bt": p["bt"],  # Burst Time
          "rem": p["bt"],  # เวลาที่เหลือต้องทำ (เริ่มต้นเท่ากับ BT)
          "ct": 0,  # Completion Time เริ่มที่ 0 (จะอัปเดตตอนทำเสร็จ)
      }  # ปิด dictionary
      for p in copy.deepcopy(processes)  # วนจากสำเนาของ process ต้นฉบับ
  ]  # ปิด list comprehension
 
  time = 0  # เวลาปัจจุบันเริ่มที่ 0
  queue = []  # ready queue (คิวของ process ที่พร้อมทำงาน)
  n = len(procs)  # จำนวน process ทั้งหมด
  completed = 0  # นับจำนวน process ที่ทำเสร็จแล้ว
  gantt_blocks = []  # list เก็บข้อมูลวาด Gantt Chart
 
  # แก้ไข: ไม่ deepcopy ซ้ำ ใช้ object เดียวกับ procs
  # เพื่อให้ curr["ct"] = time ไปอัปเดตผลลัพธ์ใน procs โดยตรง
  inarrival = sorted(procs, key=lambda x: (x["at"], x["id"]))  # list process ที่ยังไม่มาถึง เรียงตาม AT (object เดียวกับ procs)
 
  # เริ่มต้นที่ Arrival Time แรก
  if inarrival and inarrival[0]["at"] > time:  # ถ้า process แรกมาถึงหลังเวลา 0
    gantt_blocks.append(  # บันทึกช่วง Idle ตอนเริ่มต้น
        {"process": "Idle", "start": time, "end": inarrival[0]["at"]}  # Idle จากเวลา 0 ถึงเวลาที่ process แรกมา
    )  # ปิด append
    time = inarrival[0]["at"]  # ข้ามเวลาไปถึงตอน process แรกมาถึง
 
  while completed < n:  # วนจนกว่าทุก process จะเสร็จ
    # เพิ่ม Process ที่มาถึงแล้วเข้า Queue
    while inarrival and inarrival[0]["at"] <= time:  # ตราบใดที่ตัวหน้าสุดมาถึงแล้ว
      queue.append(inarrival.pop(0))  # ดึงออกจาก inarrival แล้วเอาเข้า ready queue
 
    # ถ้า Queue ยังว่างอยู่
    if not queue:  # ถ้าไม่มี process พร้อมทำงาน
      if inarrival:  # แต่ยังมี process ที่ยังไม่มาถึง
        next_at = inarrival[0]["at"]  # เวลามาถึงของ process ถัดไป
        gantt_blocks.append({"process": "Idle", "start": time, "end": next_at})  # บันทึกช่วง CPU ว่าง
        time = next_at  # ข้ามเวลาไปถึงตอนนั้น
        continue  # กลับไปต้นลูป while
      else:  # ถ้าไม่มี process เหลือเลย
        break  # ออกจากลูป (กันลูปไม่รู้จบ)
 
    # นำ Process ตัวแรกออกจาก Queue
    curr = queue.pop(0)  # ดึง process หน้าสุดของคิวมาทำงาน
    run_t = min(quantum, curr["rem"])  # เวลาที่จะรันรอบนี้ = ค่าน้อยกว่าระหว่าง quantum กับเวลาที่เหลือ
 
    start = time  # จดเวลาเริ่มรันรอบนี้
    # ทำงานตาม Time Quantum (ทีละหน่วยเวลาเพื่อให้เช็ค Process ใหม่ได้แม่นยำ)
    for _ in range(run_t):  # วนทีละ 1 หน่วยเวลา จำนวน run_t ครั้ง
      time += 1  # เวลาผ่านไป 1 หน่วย
      curr["rem"] -= 1  # เวลาที่เหลือของ process ลดลง 1
 
      # ตรวจสอบ Process ใหม่ที่เข้ามาตรงกับเวลาปัจจุบัน
      while inarrival and inarrival[0]["at"] <= time:  # ถ้ามี process มาถึงในเวลานี้
        queue.append(inarrival.pop(0))  # เอาเข้าคิวทันที (จึงเข้าคิวก่อน process ที่กำลังจะถูกส่งกลับท้ายคิว)
 
    gantt_blocks.append({"process": curr["id"], "start": start, "end": time})  # บันทึกช่วงที่รันรอบนี้ลง Gantt
 
    # Process ทำงานเสร็จ
    if curr["rem"] == 0:  # ถ้าเวลาที่เหลือเป็น 0 แปลว่าเสร็จแล้ว
      curr["ct"] = time  # บันทึก Completion Time (เขียนเข้า procs ตรง ๆ เพราะเป็น object เดียวกัน)
      completed += 1  # เพิ่มตัวนับจำนวนที่เสร็จแล้ว
    else:  # ถ้ายังไม่เสร็จ
      # ยังไม่เสร็จ นำกลับไปท้าย Queue
      queue.append(curr)  # ส่งกลับไปต่อท้ายคิว รอรอบถัดไป
 
  results = []  # list เก็บผลลัพธ์สุดท้าย
  for p in procs:  # วนทุก process
    tat = p["ct"] - p["at"]  # Turnaround Time = CT - AT
    wt = tat - p["bt"]  # Waiting Time = TAT - BT
    results.append({  # เพิ่มผลลัพธ์ของ process นี้
        "id": p["id"],  # ชื่อ process
        "at": p["at"],  # Arrival Time
        "bt": p["bt"],  # Burst Time
        "ct": p["ct"],  # Completion Time
        "tat": tat,  # Turnaround Time
        "wt": wt,  # Waiting Time
    })  # ปิด dictionary และปิด append
 
  avg_tat = sum(r["tat"] for r in results) / n  # ค่าเฉลี่ย Turnaround Time
  avg_wt = sum(r["wt"] for r in results) / n  # ค่าเฉลี่ย Waiting Time
 
  return results, avg_tat, avg_wt, gantt_blocks  # ส่งผลลัพธ์กลับไป
 
 
def get_processes_from_user():  # ฟังก์ชันรับข้อมูล process จากผู้ใช้
  """รับข้อมูลจำนวน Process และค่า Arrival Time (AT), Burst Time (BT)"""
  while True:  # วนถามจนกว่าจะกรอกถูก
    try:  # ลองแปลงค่าที่กรอกเป็นตัวเลข
      n = int(input("กรุณากรอกจำนวน Process ที่ต้องการ: "))  # รับจำนวน process แล้วแปลงเป็น int
      if n <= 0:  # ถ้ากรอก 0 หรือติดลบ
        print("❌ จำนวน Process ต้องมากกว่า 0")  # แจ้งเตือน
        continue  # ถามใหม่
      break  # กรอกถูกแล้ว ออกจากลูป
    except ValueError:  # ถ้าแปลงเป็นตัวเลขไม่ได้ (เช่น กรอกตัวอักษร)
      print("❌ กรุณากรอกเป็นตัวเลขจำนวนเต็ม")  # แจ้งเตือน
 
  processes = []  # list เก็บ process ทั้งหมด
  for i in range(1, n + 1):  # วนตั้งแต่ 1 ถึง n
    pid = f"P{i}"  # สร้างชื่อ process เช่น P1, P2, ...
 
    # รับ Arrival Time
    while True:  # วนถามจนกว่าจะกรอกถูก
      try:  # ลองแปลงเป็นตัวเลข
        at = int(input(f"กรอก Arrival Time (AT) ของ {pid}: "))  # รับ Arrival Time
        if at < 0:  # ถ้าติดลบ
          print("❌ AT ต้องไม่ติดลบ")  # แจ้งเตือน
          continue  # ถามใหม่
        break  # กรอกถูกแล้ว ออกจากลูป
      except ValueError:  # ถ้ากรอกไม่ใช่ตัวเลข
        print("❌ กรุณากรอกเป็นตัวเลขจำนวนเต็ม")  # แจ้งเตือน
 
    # รับ Burst Time
    while True:  # วนถามจนกว่าจะกรอกถูก
      try:  # ลองแปลงเป็นตัวเลข
        bt = int(input(f"กรอก Burst Time (BT) ของ {pid}: "))  # รับ Burst Time
        if bt <= 0:  # ถ้า 0 หรือติดลบ
          print("❌ BT ต้องมากกว่า 0")  # แจ้งเตือน
          continue  # ถามใหม่
        break  # กรอกถูกแล้ว ออกจากลูป
      except ValueError:  # ถ้ากรอกไม่ใช่ตัวเลข
        print("❌ กรุณากรอกเป็นตัวเลขจำนวนเต็ม")  # แจ้งเตือน
 
    processes.append({"id": pid, "at": at, "bt": bt})  # เก็บ process นี้ลง list
 
  return processes  # ส่ง list process กลับไป
 
 
def print_results(title, res, avg_tat, avg_wt, gantt_blocks):  # ฟังก์ชันแสดงผลลัพธ์ของแต่ละอัลกอริทึม
  print()  # พิมพ์บรรทัดว่าง
  print("=" * 65)  # เส้นคู่ยาว 65 ตัว
  print(f"{title:^65}")  # พิมพ์ชื่ออัลกอริทึมจัดกึ่งกลางในความกว้าง 65
  print("=" * 65)  # เส้นคู่ปิดหัวข้อ
 
  # แสดง Gantt Chart
  print_gantt_chart(gantt_blocks)  # เรียกฟังก์ชันวาด Gantt Chart
 
  # หัวตารางผลลัพธ์
  print(  # พิมพ์หัวตาราง
      f"{'Process':<12}"  # คอลัมน์ Process กว้าง 12 ชิดซ้าย
      f"{'AT':<8}"  # คอลัมน์ AT กว้าง 8
      f"{'BT':<8}"  # คอลัมน์ BT กว้าง 8
      f"{'CT':<8}"  # คอลัมน์ CT กว้าง 8
      f"{'TAT':<8}"  # คอลัมน์ TAT กว้าง 8
      f"{'WT':<8}"  # คอลัมน์ WT กว้าง 8
  )  # ปิด print
  print("-" * 65)  # เส้นขีดคั่นใต้หัวตาราง
 
  # แสดงข้อมูล Process
  for r in res:  # วนทีละ process ในผลลัพธ์
    print(  # พิมพ์ 1 แถวของตาราง
        f"{r['id']:<12}"  # ชื่อ process
        f"{r['at']:<8}"  # Arrival Time
        f"{r['bt']:<8}"  # Burst Time
        f"{r['ct']:<8}"  # Completion Time
        f"{r['tat']:<8}"  # Turnaround Time
        f"{r['wt']:<8}"  # Waiting Time
    )  # ปิด print
 
  print("-" * 65)  # เส้นขีดคั่นก่อนแสดงค่าเฉลี่ย
  # ค่าเฉลี่ย
  print(f"Average TAT : {avg_tat:.2f}")  # แสดงค่าเฉลี่ย TAT ทศนิยม 2 ตำแหน่ง
  print(f"Average WT  : {avg_wt:.2f}")  # แสดงค่าเฉลี่ย WT ทศนิยม 2 ตำแหน่ง
  print("=" * 65)  # เส้นคู่ปิดท้าย
 
 
# ============================================================
# MAIN PROGRAM
# ============================================================
 
if __name__ == "__main__":  # ทำงานส่วนนี้เมื่อรันไฟล์นี้โดยตรง (ไม่ใช่ถูก import)
  print()  # บรรทัดว่าง
  print("=" * 65)  # เส้นคู่
  print("              CPU SCHEDULING SIMULATOR")  # ชื่อโปรแกรม
  print("=" * 65)  # เส้นคู่
  print()  # บรรทัดว่าง
 
  # รับข้อมูล Process
  processes = get_processes_from_user()  # เรียกฟังก์ชันรับข้อมูล process จากผู้ใช้
 
  print()  # บรรทัดว่าง
  print("✓ รับข้อมูล Process เรียบร้อยแล้ว")  # แจ้งว่ารับข้อมูลเสร็จ
  print()  # บรรทัดว่าง
 
  # ========================================================
  # FCFS
  # ========================================================
  res, atat, awt, gantt = simulate_fcfs(processes)  # จำลอง FCFS แล้วรับผลลัพธ์ 4 ค่า
  print_results("FCFS (First Come First Serve)", res, atat, awt, gantt)  # แสดงผล FCFS
 
  # ========================================================
  # SJF
  # ========================================================
  res, atat, awt, gantt = simulate_sjf(processes)  # จำลอง SJF แล้วรับผลลัพธ์ 4 ค่า
  print_results("SJF (Shortest Job First)", res, atat, awt, gantt)  # แสดงผล SJF
 
  # ========================================================
  # ROUND ROBIN
  # ========================================================
  print()  # บรรทัดว่าง
  while True:  # วนถามจนกว่าจะกรอก quantum ถูก
    try:  # ลองแปลงเป็นตัวเลข
      quantum = int(input("กรอกค่า Time Quantum สำหรับ Round Robin: "))  # รับค่า Time Quantum
      if quantum <= 0:  # ถ้า 0 หรือติดลบ
        print("❌ Quantum ต้องมากกว่า 0")  # แจ้งเตือน
        continue  # ถามใหม่
      break  # กรอกถูกแล้ว ออกจากลูป
    except ValueError:  # ถ้ากรอกไม่ใช่ตัวเลข
      print("❌ กรุณากรอกเป็นตัวเลขจำนวนเต็ม")  # แจ้งเตือน
 
  res, atat, awt, gantt = simulate_rr_exact(processes, quantum)  # จำลอง Round Robin แล้วรับผลลัพธ์ 4 ค่า
  print_results(f"Round Robin (Time Quantum = {quantum})", res, atat, awt, gantt)  # แสดงผล Round Robin
 
  print()  # บรรทัดว่าง
  print("=" * 65)  # เส้นคู่
  print("                จบการทำงาน")  # ข้อความจบโปรแกรม
  print("=" * 65)  # เส้นคู่
 
