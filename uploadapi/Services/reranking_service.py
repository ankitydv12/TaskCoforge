import torch
import numpy as np
from sentence_transformers import CrossEncoder

class Reranking_Service:
    def cross_encoder_reranking(self,query:str,document:list[str]):

        cross_encoder = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2',
                                     device = 'cuda' if torch.cuda.is_available() else 'cpu'
                        )

        pairs = [(query , chunk) for chunk in document ]
        scores = cross_encoder.predict(pairs)

        print("Scores --> ",scores)
        print("Scores Length --> ",len(scores))

        ranked_indices = np.argsort(scores)[::-1] # Return the indices of the documents
        print("Ranked Indices --> ",ranked_indices)

        ranked_docs = [document[i] for i in ranked_indices]
        ranked_score = [scores[i] for i in ranked_indices]
        print("Ranked Docs --> ",ranked_docs)
        print("Ranked Score --> ",ranked_score)

        return ranked_docs , ranked_score

reranking_service = Reranking_Service()

if __name__ == "__main__":
    ranked_service = Reranking_Service()

    document = ['© 2024 Coforge. All rights reserved. © 2026 Coforge.', 'Leaves must be applied and approved in advance. In Bonafide exceptional situations, if  the Coforge \nEmployee is unable to seek prior approval, they may inform the immediate supervisor and apply for the \nsame immediately after returning. 7.4. During Inter-Country Transfer, the leave balance in India will be frozen and will be re-instated after \njoining back in India. The extra leaves will be lapsed basis the carry forward guideline mentioned in 7.2 \nabove. 7.5. During Inter-Country Transfer, holidays/leaves rule prevalent in that country will become applicable. 8. Child Care Leave (CCL) \n8.1. The leave period (sum total of all half-day leaves) will be considered as Leave without Pay. There \nwill be proportionate deduction in entitlements as mentioned in clause 9.3.', 'No encashment \nof leaves in the \nevent of \nseparation or \ncompletion of \nassignment/training \nNo provision \nof taking \nadvance \nleaves \nImmediate \nSupervisor \n4. Leave Categories and Entitlements for Regular and Retainers at Coforge \n \nLeave Type Eligibility Entitlement Weekly \nHolidays \nduring leave \nNotice Period \nTreatment \nApproving \nAuthority \nRemarks \n \n \nEarned  \nLeave \nAll Regular  \n& Retainers \n \n24 days per year @ 2 days per \nmonth starting from April of every \nFinancial Year. Not Counted \nMaximum 10 \ndays’ leave can \nbe availed \nsubject to \nsupervisor’s \napproval \n \n \nImmediate \nSupervisor \n \nLeaves will be credited on \nthe 1st of the month for \nthe previous month. Advance  \nLeave \n \nAll Regular \n& Retainers \n15 days leave in case of: \ni) Own Marriage \nii) Self Sickness \niii) Furlough \n7 day’s leave in case of: \ni) Academic Examination \n \n \nNot Counted \n \nCannot be \navailed \n \nImmediate \nSupervisor \n \n \nNA \n \n \n \n     Paternity \nLeave \n \nAll Regular and \nRetainer male \nemployees who \nbecome fathers \nduring their \nemployment with \nCoforge Limited  \n1) 5 continuous working days’ \nleave for first three children \nborn/adopted during the \nCoforge employee tenure \nwith Coforge Limited. 2) Leaves have to be availed \nwithin 12 months’ of the \nbirth/adoption of Child  \n \n \n \n \n \n Not Counted \n \n \n \nCannot be \navailed \n \n \n \n \nImmediate \nSupervisor \n \n \nEmployee must update \ntheir child details under \nfamily details on iEngage \nbefore they apply for \nPaternity Leave. Child Care \nLeave (CCL) \n \n(Only for \nRegular \nemployees) \n \ni) Employees having \n2 years’ of service \nin Coforge Limited \nat the time of \nstarting CCL. Maximum 6 months half day \nworking on half pay, for first two \nchildren. Counted \n \nCannot be \navailed \n \nSupervisor \n+ Reviewing \nManager + \n1) Employee must \ninform their \nrespective \nBusiness HRs \nbefore \ncommencement of \nthe leave.', '8.3. If the amount of deduction for any availed scheme (CLA, Car Scheme, etc.) exceeds the monthly \nsalary, the shortfall will be paid by the Coforge Employee through cheque in advance. 8.4. In case of any work -related travel requirement/training program, the Coforge Employee is \nrequired to work full day and the entitlements will be as per the travel policy. 9.', 'LEAVE AND HOLIDAY POLICY- INDIA \n© 2026 Coforge 5 \n \n \n \n6. Guidelines: \n6.1. Leave is not a right but a privilege and needs prior approval as per defined guidelines. 6.2. Leaves can be applied from iEngage >> My Data >> Applications (Leave/Voucher) >> Create \nDocument >> Leave \n7. Earned Leaves \n7.1. Pro-rata leave credit is done for all new joiners during the month as illustrated below: \n \nNumber of days worked in the \nmonth of Joining \n23 days or more 16 – 22 days 8 – 15 days 1-7 days \nLeaves Credited 2 1.5 1 0.5 \n7.2. A maximum of 10 days of un-availed leaves can be carried forward to the next financial year, subject to \na maximum of 45 days.']

    ranked_service.cross_encoder_reranking(
        "leaves in a months" , document
    ) 
