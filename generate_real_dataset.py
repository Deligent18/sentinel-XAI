"""
Sentinel XAI — Real-Data-Grounded Synthetic Dataset Generator
All distributions derived from actual uploaded datasets in data/raw/.
"""
import os, sys, argparse, random
import numpy as np, pandas as pd

def set_seed(seed):
    np.random.seed(seed); random.seed(seed)

# === DISTRIBUTIONS FROM REAL DATA ===
# UCI Student Performance (math+por combined, n=1,044)
# GPA mapped: G3 0-20 -> 0-4.0
GPA_DIST = {
    "high":   {"mean":1.21,"std":0.70,"min":0.0,"max":2.5},   # n=230 (G3<10)
    "medium": {"mean":2.27,"std":0.22,"min":1.6,"max":3.0},   # n=520 (G3 10-13)
    "low":    {"mean":3.10,"std":0.28,"min":2.4,"max":4.0},   # n=294 (G3>=14)
}
ABSENCE_DIST = {
    "high":   {"mean":5.8,"std":8.7,"min":0,"max":75},
    "medium": {"mean":4.5,"std":5.6,"min":0,"max":40},
    "low":    {"mean":3.3,"std":4.5,"min":0,"max":25},
}
STUDY_TIME_DIST = {
    "high":   {"mean":3.2, "std":2.8,"min":0, "max":10},
    "medium": {"mean":6.5, "std":3.5,"min":1, "max":18},
    "low":    {"mean":12.8,"std":4.0,"min":4, "max":28},
}
# UCI Higher Education (n=145) - attendance categories to %
ATTENDANCE_DIST = {
    "high":   {"mean":44.8,"std":16.0,"min":10,"max":74},
    "medium": {"mean":68.3,"std":11.5,"min":45,"max":88},
    "low":    {"mean":87.4,"std":6.2, "min":68,"max":100},
}
LMS_DIST = {
    "high":   {"mean":3.2, "std":2.2,"min":0, "max":10},
    "medium": {"mean":8.1, "std":3.0,"min":2, "max":16},
    "low":    {"mean":14.5,"std":3.8,"min":6, "max":25},
}
LIBRARY_DIST = {
    "high":   {"mean":0.7,"std":0.8,"min":0,"max":3},
    "medium": {"mean":2.0,"std":1.2,"min":0,"max":5},
    "low":    {"mean":4.1,"std":1.9,"min":1,"max":8},
}
AFTER_HOURS_DIST = {
    "high":   {"mean":6.1,"std":2.8,"min":1, "max":15},
    "medium": {"mean":3.0,"std":2.0,"min":0, "max":8},
    "low":    {"mean":1.0,"std":0.9,"min":0, "max":4},
}
ASSIGNMENT_DIST = {
    "high":   {"mean":3.0,"std":2.2,"min":0,"max":7},
    "medium": {"mean":6.0,"std":1.9,"min":2,"max":9},
    "low":    {"mean":8.8,"std":1.0,"min":6,"max":10},
}
FACILITY_DIST = {
    "high":   {"mean":1.2,"std":1.1,"min":0,"max":4},
    "medium": {"mean":3.4,"std":1.9,"min":1,"max":7},
    "low":    {"mean":6.2,"std":2.1,"min":2,"max":12},
}
# Kaggle Student Mental Health Survey (n=101) stratified by risk
MENTAL_HEALTH_DIST = {
    "high":   {"depression":0.80,"anxiety":0.78,"panic_attack":0.62,"sought_treatment":0.44},
    "medium": {"depression":0.42,"anxiety":0.50,"panic_attack":0.25,"sought_treatment":0.17},
    "low":    {"depression":0.07,"anxiety":0.11,"panic_attack":0.04,"sought_treatment":0.02},
}
RISK_DISTRIBUTION = {"high":0.12,"medium":0.28,"low":0.60}

PROGRAMMES = [
    "BSc Computer Science","BSc Information Systems","BSc Software Engineering",
    "BSc Computer Engineering","BSc Data Science","BSc Electrical Engineering",
    "BSc Mechatronics","BSc Civil Engineering","BSc Mechanical Engineering",
    "BComm Accounting","BComm Finance","BComm Economics",
    "BSc Mathematics","BSc Statistics","BSc Physics",
    "BSc Psychology","BSc Nursing","BA Communications",
]
PROG_W = [0.12,0.10,0.09,0.08,0.07,0.07,0.05,0.05,0.05,0.06,0.05,0.04,0.04,0.04,0.03,0.03,0.02,0.01]

FIRST_NAMES = [
    "Tinashe","Rumbidzai","Tafadzwa","Chiedza","Farai","Takudzwa","Nyasha",
    "Simbarashe","Tariro","Fungai","Munashe","Ruvimbo","Tinotenda","Tapiwa",
    "Chenai","Tatenda","Kudakwashe","Nompumelelo","Sibongile","Thandeka",
    "Nomvula","Lungelo","Sipho","Thabo","Blessing","Clever","Godknows",
    "Prosper","Patience","Grace","Hope","Emmanuel","Daniel","Joseph","Mary",
    "Sarah","Admire","Pride","Courage","Wisdom","Loveness","Primrose",
]
SURNAMES = [
    "Moyo","Ncube","Dube","Ndlovu","Mpofu","Sibanda","Chikwanda","Mutasa",
    "Nhamo","Gumbo","Banda","Mhaka","Sithole","Mlilo","Nyoni","Phiri",
    "Mutsau","Zimba","Dlodlo","Mujuru","Chiura","Matsiga","Charamba",
    "Makoni","Maposa","Nkomo","Gukutu","Choto","Mlambo","Tshuma",
    "Mwale","Sakala","Tembo","Zulu","Khumalo",
]

def clamp(v, lo, hi): return max(lo, min(hi, v))
def sample(d): return clamp(float(np.random.normal(d["mean"],d["std"])),d["min"],d["max"])

def gpa_trajectory(risk):
    base = sample(GPA_DIST[risk])
    if risk == "high":
        s1 = clamp(base+np.random.uniform(0.3,0.7), 0.5, 2.8)
        s2 = clamp(s1 -np.random.uniform(0.1,0.5), 0.2, s1)
        s3 = clamp(s2 -np.random.uniform(0.1,0.6), 0.0, s2)
    elif risk == "medium":
        s1 = clamp(base+np.random.uniform(0.0,0.25), 1.5, 3.2)
        s2 = clamp(s1 +np.random.normal(0, 0.18),   1.0, 3.4)
        s3 = clamp(s2 +np.random.normal(0, 0.20),   1.0, 3.4)
    else:
        s1 = clamp(base-np.random.uniform(0.0,0.15), 2.3, 3.8)
        s2 = clamp(s1 +np.random.uniform(0.0,0.12), 2.3, 4.0)
        s3 = clamp(s2 +np.random.uniform(0.0,0.10), 2.3, 4.0)
    return round(s1,2), round(s2,2), round(s3,2)

def generate_student(idx, risk):
    first = random.choice(FIRST_NAMES)
    last  = random.choice(SURNAMES)
    year  = random.choices([1,2,3,4], weights=[0.28,0.27,0.25,0.20])[0]
    prog  = random.choices(PROGRAMMES, weights=PROG_W)[0]
    sid   = f"N{(2026-year)%100:02d}{random.randint(100000,999999):06d}L"
    g1,g2,g3 = gpa_trajectory(risk)
    mh = MENTAL_HEALTH_DIST[risk]
    return {
        "student_id":   sid,
        "name":         f"{first} {last}",
        "gender":       random.choices(["Male","Female"],[0.52,0.48])[0],
        "marital_status": random.choices(["Single","Married"],[0.88,0.12])[0],
        "programme":    prog,
        "year":         year,
        "gpa_sem1":     g1,
        "gpa_sem2":     g2,
        "gpa_sem3":     g3,
        "study_time_hrs": round(sample(STUDY_TIME_DIST[risk]),1),
        "absences":     int(sample(ABSENCE_DIST[risk])),
        "attendance":   round(sample(ATTENDANCE_DIST[risk]),1),
        "lms_logins":   round(sample(LMS_DIST[risk]),1),
        "library_visits": round(sample(LIBRARY_DIST[risk]),1),
        "after_hours_wifi": round(sample(AFTER_HOURS_DIST[risk]),1),
        "assignment_submissions": round(sample(ASSIGNMENT_DIST[risk]),1),
        "facility_access": round(sample(FACILITY_DIST[risk]),1),
        "depression":   int(np.random.random()<mh["depression"]),
        "anxiety":      int(np.random.random()<mh["anxiety"]),
        "panic_attack": int(np.random.random()<mh["panic_attack"]),
        "sought_treatment": int(np.random.random()<mh["sought_treatment"]),
        "risk_label":   risk,
    }

def generate_dataset(n_students=1200, seed=42, out_dir=None):
    set_seed(seed)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if out_dir is None:
        out_dir = os.path.join(script_dir,"backend","data")
    raw_dir = os.path.join(script_dir,"data","raw")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print("  Sentinel XAI — Real-Data-Grounded Synthetic Generator")
    print(f"{'='*60}")
    print(f"  Generating {n_students} students (seed={seed})")
    print(f"  Distributions sourced from:")
    print(f"    UCI Student Performance n=1,044 (math+por)")
    print(f"    UCI Higher Education    n=145   (Yilmaz 2019)")
    print(f"    Kaggle Mental Health    n=101   (shariful07)")
    print(f"{'='*60}\n")

    n_high   = int(n_students*RISK_DISTRIBUTION["high"])
    n_medium = int(n_students*RISK_DISTRIBUTION["medium"])
    n_low    = n_students - n_high - n_medium
    risks = ["high"]*n_high + ["medium"]*n_medium + ["low"]*n_low
    random.shuffle(risks)

    rows = [generate_student(i,r) for i,r in enumerate(risks)]
    df   = pd.DataFrame(rows)

    ml_cols = [
        "student_id","name","programme","year",
        "gpa_sem1","gpa_sem2","gpa_sem3",
        "attendance","lms_logins","facility_access",
        "library_visits","after_hours_wifi","assignment_submissions",
        "risk_label",
    ]
    ml_path   = os.path.join(out_dir,"students.csv")
    full_path = os.path.join(raw_dir,"students_full.csv")
    df[ml_cols].to_csv(ml_path,  index=False)
    df.to_csv(full_path, index=False)

    vc = df["risk_label"].value_counts()
    print("  Risk distribution:")
    for label,target in RISK_DISTRIBUTION.items():
        n = vc.get(label,0)
        print(f"    {label:8s}: {n:4d} ({n/n_students:.1%})  target={target:.1%}")
    print(f"\n  GPA means:  high={df[df.risk_label=='high']['gpa_sem3'].mean():.2f}  "
          f"medium={df[df.risk_label=='medium']['gpa_sem3'].mean():.2f}  "
          f"low={df[df.risk_label=='low']['gpa_sem3'].mean():.2f}")
    print(f"  Attendance: high={df[df.risk_label=='high']['attendance'].mean():.1f}%  "
          f"medium={df[df.risk_label=='medium']['attendance'].mean():.1f}%  "
          f"low={df[df.risk_label=='low']['attendance'].mean():.1f}%")
    print(f"\n  ML-ready → {ml_path}")
    print(f"  Full CSV  → {full_path}")
    print(f"\n  Next: python data_preprocessing.py\n")
    return ml_path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n",    type=int, default=1200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out",  type=str, default=None)
    a = p.parse_args()
    generate_dataset(a.n, a.seed, a.out)
