"""
Seed demo data for the Oncodash frontend.

Creates ClinicalData + TimelineRecord entries with realistic
ovarian cancer patient data so the UI renders fully.

Usage:
    python manage.py seed_demo_data
    python manage.py seed_demo_data --clear   # wipe existing data first
"""

import random
import math
from django.core.management.base import BaseCommand
from clin_overview.models import ClinicalData, TimelineRecord


# ── Patient profiles ──────────────────────────────────────────────

PATIENTS = [
    dict(patient_id=1001, cohort_code="DEC-001", age=62, height=165, weight=66,
         stage="IIIC", strategy="NACT", survival="ALIVE", progression=True,
         brca="BRCA1BLOOD", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=True, trial_name="PAOLA"),
    dict(patient_id=1002, cohort_code="DEC-002", age=71, height=158, weight=72,
         stage="IVA", strategy="NACT", survival="DEATHCANCER", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PARTIAL",
         phase="PROGRESSION", trial=False, trial_name=None),
    dict(patient_id=1003, cohort_code="DEC-003", age=55, height=170, weight=60,
         stage="IIIC", strategy="PDS", survival="ALIVE", progression=False,
         brca="BRCA2BLOOD", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=False, trial_name=None),
    dict(patient_id=1004, cohort_code="DEC-004", age=67, height=162, weight=78,
         stage="IIIB", strategy="NACT", survival="ALIVE", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PARTIAL",
         phase="FOLLOWUP_AFTER_PROG_TREATMENT", trial=True, trial_name="PRIMA"),
    dict(patient_id=1005, cohort_code="DEC-005", age=48, height=175, weight=64,
         stage="IIIC", strategy="PDS", survival="ALIVE", progression=False,
         brca="BRCA1TUMOR", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=False, trial_name=None),
    dict(patient_id=1006, cohort_code="DEC-006", age=73, height=155, weight=68,
         stage="IVB", strategy="NACT", survival="DEATHCANCER", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PROGRESSIVE",
         phase="PROGRESSION_ACTIVE_TREATMENT_ENDED", trial=False, trial_name=None),
    dict(patient_id=1007, cohort_code="DEC-007", age=59, height=168, weight=70,
         stage="IIIC", strategy="NACT", survival="ALIVE", progression=True,
         brca="BRCA1BLOOD", hrd="HRD", outcome="COMPLETE",
         phase="PARP_MAINTENANCE_AFTER_PROG", trial=True, trial_name="AVANOVA"),
    dict(patient_id=1008, cohort_code="DEC-008", age=64, height=160, weight=82,
         stage="IVA", strategy="NACT", survival="DEATHOTHER", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PARTIAL",
         phase="PROGRESSION", trial=False, trial_name=None),
    dict(patient_id=1009, cohort_code="DEC-009", age=51, height=172, weight=58,
         stage="IIIA2", strategy="PDS", survival="ALIVE", progression=False,
         brca="BRCA2TUMOR", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=False, trial_name=None),
    dict(patient_id=1010, cohort_code="DEC-010", age=77, height=156, weight=74,
         stage="IIIC", strategy="NACT", survival="DEATHCANCER", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PROGRESSIVE",
         phase="PROGRESSION", trial=False, trial_name=None),
    dict(patient_id=1011, cohort_code="DEC-011", age=45, height=180, weight=62,
         stage="IIB", strategy="PDS", survival="ALIVE", progression=False,
         brca="BRCA1BLOOD", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=True, trial_name="IMAGYN"),
    dict(patient_id=1012, cohort_code="DEC-012", age=69, height=163, weight=76,
         stage="IIIC", strategy="NACT", survival="ALIVE", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PARTIAL",
         phase="FOLLOWUP_AFTER_PROG_TREATMENT", trial=False, trial_name=None),
    dict(patient_id=1013, cohort_code="DEC-013", age=57, height=167, weight=65,
         stage="IVA", strategy="NACT", survival="ALIVE", progression=True,
         brca="BRCA1TUMOR", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=True, trial_name="DUOO"),
    dict(patient_id=1014, cohort_code="DEC-014", age=66, height=159, weight=71,
         stage="IIIC", strategy="PDS", survival="DEATHCANCER", progression=True,
         brca="NOBRCA", hrd="HRP", outcome="PARTIAL",
         phase="PROGRESSION_ACTIVE_TREATMENT_ENDED", trial=False, trial_name=None),
    dict(patient_id=1015, cohort_code="DEC-015", age=53, height=174, weight=59,
         stage="IIIC", strategy="NACT", survival="ALIVE", progression=False,
         brca="BRCA2BLOOD", hrd="HRD", outcome="COMPLETE",
         phase="FOLLOW_UP", trial=False, trial_name=None),
]


# ── Lab value generators ──────────────────────────────────────────

def _jitter(val, pct=0.1):
    return val * (1 + random.uniform(-pct, pct))


def _generate_lab_series(name, n_days, has_progression, progression_day):
    """Generate sparse lab measurements at semi-regular intervals."""
    measurements = []
    day = 0
    while day < n_days:
        if name == "ca125":
            if day < 30:
                val = _jitter(random.uniform(800, 5000))
            elif day < 150:
                progress = (day - 30) / 120.0
                val = _jitter(800 * math.exp(-3 * progress) + 20)
            elif has_progression and day > progression_day - 30:
                rise = (day - (progression_day - 30)) / 60.0
                val = _jitter(30 + 200 * rise)
            else:
                val = _jitter(random.uniform(10, 40))
        elif name == "hb":
            base = random.uniform(125, 145)
            if 20 < day < 160:
                dip = 15 * math.sin(math.pi * (day - 20) / 140)
                val = _jitter(base - dip)
            else:
                val = _jitter(base)
        elif name == "neut":
            base = random.uniform(3.5, 5.5)
            if 20 < day < 160:
                cycle_pos = ((day - 20) % 21) / 21.0
                dip = 2.0 * math.sin(math.pi * cycle_pos)
                val = max(0.3, _jitter(base - dip))
            else:
                val = _jitter(base)
        elif name == "leuk":
            base = random.uniform(5.0, 8.0)
            if 20 < day < 160:
                cycle_pos = ((day - 20) % 21) / 21.0
                dip = 3.0 * math.sin(math.pi * cycle_pos)
                val = max(1.0, _jitter(base - dip))
            else:
                val = _jitter(base)
        elif name == "platelets":
            base = random.uniform(200, 300)
            if 20 < day < 160:
                cycle_pos = ((day - 20) % 21) / 21.0
                dip = 80 * math.sin(math.pi * cycle_pos)
                val = max(50, _jitter(base - dip))
            else:
                val = _jitter(base)
        else:
            val = 0

        measurements.append((day, round(val, 1)))
        if day < 160:
            day += random.randint(7, 21)
        else:
            day += random.randint(21, 42)

    return measurements


# ── Main command ──────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed demo data: 15 patients with clinical data and timeline records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true",
            help="Delete all existing ClinicalData and TimelineRecord before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            TimelineRecord.objects.all().delete()
            ClinicalData.objects.all().delete()

        record_id = 100000

        for p in PATIENTS:
            bmi = round(p["weight"] / (p["height"] / 100.0) ** 2, 1)
            followup = random.randint(400, 1500)
            days_to_prog = random.randint(200, 600) if p["progression"] else None
            days_to_death = None
            if p["survival"] in ("DEATHCANCER", "DEATHOTHER", "DEATHUNKNOWN"):
                days_to_death = random.randint(
                    (days_to_prog or 300) + 60,
                    (days_to_prog or 300) + 400,
                )
                followup = days_to_death

            clinical = ClinicalData.objects.create(
                patient_id=p["patient_id"],
                cohort_code=p["cohort_code"],
                age_at_diagnosis=p["age"],
                height_at_diagnosis=p["height"],
                weight_at_diagnosis=p["weight"],
                bmi_at_diagnosis=bmi,
                histology="HGSOC",
                stage=p["stage"],
                treatment_strategy=p["strategy"],
                primary_therapy_outcome=p["outcome"],
                survival=p["survival"],
                progression=p["progression"],
                current_treatment_phase=p["phase"],
                brca_mutation_status=p["brca"],
                hr_signature_pretreatment_wgs=p["hrd"],
                hr_signature_per_patient=p["hrd"],
                hrd_myriad_status="HRDPOSITIVE" if p["hrd"] == "HRD" else "HRDNEGATIVE",
                clinical_trial=p["trial"],
                drug_trial_name=p["trial_name"],
                drug_trial_unblinded=p["trial"],
                followup_time=followup,
                days_to_progression=days_to_prog,
                days_to_death=days_to_death,
                platinum_free_interval=random.randint(100, 400) if p["progression"] else None,
                wgs_available=random.choice([True, True, False]),
                sequencing_available=True,
                paired_fresh_samples_available=random.choice([True, False]),
                residual_tumor_pds=random.choice(["ZERO", "ZEROTEN", None]),
                residual_tumor_ids=random.choice(["ZERO", "ZEROTEN", None]),
                debulking_surgery_ids=p["strategy"] == "NACT",
                operation1_cancelled=False,
                operation2_cancelled=random.choice([False, False, True]),
                previous_cancer=False,
                chronic_illnesses_at_dg=random.choice([True, False]),
                chronic_illnesses_type="HYPERTENSION" if random.random() > 0.6 else None,
                maintenance_therapy=random.choice(["BEVACIZUMAB", "PARPI", None]),
                germline_pathogenic_variant=p["brca"].replace("BLOOD", "").replace("TUMOR", "") if "BRCA" in p["brca"] and p["brca"] != "NOBRCA" else None,
            )

            n_days = followup + 15
            progression_day = days_to_prog or n_days

            # ── Laboratory records ────────────────────────────
            for biomarker in ["ca125", "hb", "neut", "leuk", "platelets"]:
                series = _generate_lab_series(
                    biomarker, n_days, p["progression"], progression_day
                )
                for day, result in series:
                    record_id += 1
                    TimelineRecord.objects.create(
                        external_record_id=record_id,
                        patient=clinical,
                        event="laboratory",
                        name=biomarker,
                        date_relative=day,
                        result=result,
                    )

            # ── Diagnosis event (day 0) ───────────────────────
            record_id += 1
            TimelineRecord.objects.create(
                external_record_id=record_id,
                patient=clinical,
                event="diagnosis",
                name="diagnosis",
                date_relative=0,
            )

            # ── Chemotherapy doses ────────────────────────────
            chemo_drugs = ["carboplatin", "paclitaxel"]
            chemo_start = random.randint(14, 28)
            for cycle in range(random.randint(5, 8)):
                day = chemo_start + cycle * 21
                for drug in chemo_drugs:
                    record_id += 1
                    TimelineRecord.objects.create(
                        external_record_id=record_id,
                        patient=clinical,
                        event="chemotherapy_dose",
                        name=drug,
                        date_relative=day,
                    )

            # ── Last date of primary therapy ──────────────────
            last_chemo_day = chemo_start + (random.randint(5, 8) - 1) * 21
            record_id += 1
            TimelineRecord.objects.create(
                external_record_id=record_id,
                patient=clinical,
                event="last_date_of_primary_therapy",
                name="last_date_of_primary_therapy",
                date_relative=last_chemo_day + 7,
            )

            # ── Progression event ─────────────────────────────
            if p["progression"] and days_to_prog:
                record_id += 1
                TimelineRecord.objects.create(
                    external_record_id=record_id,
                    patient=clinical,
                    event="primary_progression",
                    name="primary_progression",
                    date_relative=days_to_prog,
                )

            # ── Death event ───────────────────────────────────
            if days_to_death:
                record_id += 1
                TimelineRecord.objects.create(
                    external_record_id=record_id,
                    patient=clinical,
                    event="death",
                    name="death",
                    date_relative=days_to_death,
                )

            # ── Fresh samples ─────────────────────────────────
            record_id += 1
            TimelineRecord.objects.create(
                external_record_id=record_id,
                patient=clinical,
                event="fresh_sample",
                name="primary_tissue",
                date_relative=0,
            )
            if p["strategy"] == "NACT":
                record_id += 1
                TimelineRecord.objects.create(
                    external_record_id=record_id,
                    patient=clinical,
                    event="fresh_sample",
                    name="ids_tissue",
                    date_relative=random.randint(80, 130),
                )

            # ── Fresh sample sequenced ────────────────────────
            record_id += 1
            TimelineRecord.objects.create(
                external_record_id=record_id,
                patient=clinical,
                event="fresh_sample_sequenced",
                name="sequenced_primary",
                date_relative=random.randint(10, 40),
            )

            # ── ctDNA samples ─────────────────────────────────
            for ctdna_day in [random.randint(5, 15), random.randint(150, 250)]:
                if ctdna_day < n_days:
                    record_id += 1
                    TimelineRecord.objects.create(
                        external_record_id=record_id,
                        patient=clinical,
                        event="ctdna_sample",
                        name="ctdna",
                        date_relative=ctdna_day,
                    )

            # ── Radiology (CT scans) ──────────────────────────
            ct_day = 60
            while ct_day < n_days:
                record_id += 1
                TimelineRecord.objects.create(
                    external_record_id=record_id,
                    patient=clinical,
                    event="radiology",
                    name="CT",
                    date_relative=ct_day,
                )
                ct_day += random.randint(60, 120)

            # ── Plasma samples ────────────────────────────────
            for plasma_day in [random.randint(3, 10), random.randint(90, 140)]:
                if plasma_day < n_days:
                    record_id += 1
                    TimelineRecord.objects.create(
                        external_record_id=record_id,
                        patient=clinical,
                        event="tykslab_plasma",
                        name="plasma_sample",
                        date_relative=plasma_day,
                    )

            self.stdout.write(f"  Created patient {p['cohort_code']} (id={p['patient_id']})")

        total_patients = ClinicalData.objects.count()
        total_records = TimelineRecord.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {total_patients} patients, {total_records} timeline records."
        ))
