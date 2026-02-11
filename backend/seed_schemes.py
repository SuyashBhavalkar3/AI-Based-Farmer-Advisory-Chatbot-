"""Seed script to populate government schemes in the database."""

from sqlalchemy.orm import Session
from database.base import init_db, get_db, engine
from database.models import Scheme, SchemeDocument

# Initialize database
init_db()

# Connect to database
from database.base import SessionLocal
db = SessionLocal()

try:
    # Clear existing schemes
    db.query(SchemeDocument).delete()
    db.query(Scheme).delete()
    db.commit()
    
    # Government schemes data
    schemes_data = [
        {
            "name": "PM Kisan Samman Nidhi",
            "description": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a central sector scheme with 100% funding by Government of India. The scheme aims to supplement the financial needs of the farmer for procuring essential inputs to ensure proper health and productivity of crops.",
            "eligibility": "• All landholding farmer families\n• Valid Aadhar Card\n• Indian citizen\n• Age: 18 years or above\n• Excluded: Income tax payers, beneficiaries of higher income support schemes",
            "benefits": "• ₹6,000 per year (₹2,000 per installment)\n• Direct transfer to bank account in 4-monthly installments\n• No conditions on crop selection\n• Applicable to all crops",
            "application_process": "1. Register on PM-KISAN portal or through CSC\n2. Verify land records (Aadhar linked)\n3. Bank account must be operational\n4. Submit required documents\n5. Approval and fund transfer to bank account\n6. Installments credited automatically every 4 months",
            "scheme_type": "Income Support"
        },
        {
            "name": "Pradhan Mantri Fasal Bima Yojana",
            "description": "Pradhan Mantri Fasal Bima Yojana (PMFBY) is a crop insurance scheme designed to protect farmers against loss/damage arising out of unforeseen events like natural calamities, pests, and diseases beyond the control of the farmers.",
            "eligibility": "• All farmers - individual and tenant farmers\n• Sharecroppers\n• Agricultural workers\n• Landless farmers\n• No income limit\n• Participating banks or Self Help Groups (SHGs)",
            "benefits": "• Comprehensive insurance coverage for all crops\n• Claims up to ₹1,00,000 per hectare\n• Low premium rates (1.5-2% for crops, 2-3.5% for horticulture)\n• Maximum: ₹10 crore per applicant\n• Claims settled within 2 months",
            "application_process": "1. Contact CSC, bank, or insurer office\n2. Select crop and season\n3. Provide land documents (Aadhar, Bank account)\n4. Pay premium through bank\n5. Submit claim forms for losses within 72 hours\n6. Verification and claim settlement",
            "scheme_type": "Insurance"
        },
        {
            "name": "Kisan Credit Card",
            "description": "Kisan Credit Card (KCC) is a credit delivery scheme that enables farmers to access affordable credit on time from banks for their cultivation and other farming activities. It provides timely and adequate credit support.",
            "eligibility": "• Individual farmers (sole proprietors)\n• Tenant farmers\n• Share-croppers\n• Landless farmers\n• SHGs/JLGs\n• Age: 18-75 years\n• Fixed assets as collateral (for amount > ₹50,000)",
            "benefits": "• Flexible credit limit (₹25,000 to ₹10,00,000+)\n• Lower interest rates (7-8% per annum)\n• Easy renewal process\n• No collateral for loans up to ₹50,000\n• 3-year validity\n• Overdraft facility available",
            "application_process": "1. Visit nearest bank branch\n2. Submit KCC application form with photo ID & address proof\n3. Land records (7/12 extract) and bank passbook\n4. Bank conducts inspection\n5. Process and issue KCC card within 14 days\n6. Loan disbursement as per requirement",
            "scheme_type": "Credit"
        },
        {
            "name": "Pradhan Mantri Irrigation Yojana",
            "description": "Accelerated Irrigation Benefits Program (AIBP) provides assured irrigation to agricultural lands through constructing and maintaining irrigation infrastructure across the country, improving agricultural productivity.",
            "eligibility": "• Farmers with agricultural land in command areas of irrigation projects\n• Farmers in drought-prone or water-scarce regions\n• No income limit\n• Tenant farmers and small/marginal farmers preferred",
            "benefits": "• Subsidized irrigation infrastructure (50-90% subsidy)\n• Increased crop productivity through assured water supply\n• Per hectare benefit: ₹10,000-₹40,000\n• Free water supply for agriculture\n• Reduced input costs",
            "application_process": "1. Contact block agriculture office\n2. Enroll in irrigation command area\n3. Provide land records and identity proof\n4. Select irrigation source\n5. Join farmers' cooperative group\n6. Infrastructure development and water allocation",
            "scheme_type": "Infrastructure"
        },
        {
            "name": "Paramparagat Krishi Vikas Yojana",
            "description": "Paramparagat Krishi Vikas Yojana (PKVY) promotes organic farming through a cluster approach and encourages sustainability in agriculture. It aims to shift farmers from chemical-intensive farming to organic farming.",
            "eligibility": "• Individual farmers interested in organic farming\n• Farmers' groups and clusters (minimum 50 members)\n• Minimum land: 0.5 hectare\n• For clusters: 50-200 farmers with 50-100 hectares",
            "benefits": "• ₹50,000 per hectare subsidy for 3 years\n• ₹10,000 per hectare for external inputs\n• Certification support and organic product marketing assistance\n• Reduced chemical expenditure by 50-60%\n• Premium prices for organic produce (15-30% higher)",
            "application_process": "1. Form group of farmers or apply individually\n2. Submit application to agricultural department\n3. Provide land details and farming history\n4. Training on organic farming practices\n5. Soil and water testing\n6. Receive subsidy in instalments over 3 years",
            "scheme_type": "Organic Farming"
        },
        {
            "name": "Rashtriya Krishi Vikas Yojana",
            "description": "Rashtriya Krishi Vikas Yojana (RKVY) aims to accelerate agricultural growth through state-led projects. It focuses on promotion of high-value agriculture, horticulture, and allied sectors.",
            "eligibility": "• State governments and registered farmer groups\n• Farmers interested in high-value agriculture\n• Minimum 0.5 hectare land\n• Bank loans upto ₹25,000 per hectare available",
            "benefits": "• 50% subsidy on equipment and infrastructure\n• Production increase up to 300%\n• Value addition infrastructure support\n• Technology demonstration plots\n• Market linkage and cold chain facilities",
            "application_process": "1. State government develops project proposals\n2. Farmer groups register with agriculture department\n3. Project appraisal by technical committee\n4. Fund release for implementation\n5. Bank provides 50% loan + 50% subsidy\n6. Monitoring and evaluation",
            "scheme_type": "Agricultural Development"
        }
    ]
    
    # Create schemes
    created_schemes = []
    for scheme_data in schemes_data:
        scheme = Scheme(**scheme_data)
        db.add(scheme)
        db.flush()  # Get the ID without committing
        created_schemes.append(scheme)
    
    db.commit()
    
    print(f"✅ Successfully created {len(created_schemes)} schemes!")
    for scheme in created_schemes:
        print(f"  • {scheme.name} (ID: {scheme.id})")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error seeding schemes: {str(e)}")
    raise
finally:
    db.close()
