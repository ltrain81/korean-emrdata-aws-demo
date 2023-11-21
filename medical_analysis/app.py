#!/usr/bin/env python3
import os
from aws_cdk import App

from medical_analysis.medical_analysis_stack import MedicalAnalysisStack

app = App()
MedicalAnalysisStack(app, "MedicalAnalysisStack")

app.synth()
