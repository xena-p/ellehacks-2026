# game/gemini_utils.py
import os
import json
import random
from google import genai
from google.genai import types
from ninja import Schema
from typing import List
from pydantic import ValidationError

class QuestionSchema(Schema):
    question: str
    options: List[str]
    answer: str
    explanation: str


def get_gemini_client():
    """Returns the client only when called, preventing startup hangs."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in your environment variables.")
    
    return genai.Client(api_key=api_key)

def generate_question(level: int) -> dict:
    fallback_questions = {
    1: [
        {
            "question": "What is a 'Need'?",
            "options": ["A new toy", "A video game", "Healthy food", "A fancy hat"],
            "answer": "Healthy food",
            "explanation": "Needs are things you must have to live and stay healthy!"
        },
        {
            "question": "What does it mean to 'Save'?",
            "options": [
                "Spending all your money",
                "Keeping money for later",
                "Giving money away",
                "Losing your wallet"
            ],
            "answer": "Keeping money for later",
            "explanation": "Saving means keeping money to use in the future!"
        },
        {
            "question": "Which is a 'Want'?",
            "options": ["Clean water", "A place to live", "A new video game", "Healthy food"],
            "answer": "A new video game",
            "explanation": "A want is something you would like to have but do not need to live."
        },
        {
            "question": "Why is it good to save money?",
            "options": ["To spend it all today", "To use it later", "To lose it", "To hide it forever"],
            "answer": "To use it later",
            "explanation": "Saving gives you money to use for future needs, wants, or goals."
        },
        {
            "question": "What can you use money to buy?",
            "options": ["Only toys", "Only food", "Goods and services", "Nothing"],
            "answer": "Goods and services",
            "explanation": "Money can be used to pay for things you buy and services people provide."
        },
        {
            "question": "Which one is a need?",
            "options": ["Candy", "A warm coat", "A toy", "A video game"],
            "answer": "A warm coat",
            "explanation": "A warm coat can help protect you from cold weather, making it a need in cold conditions."
        },
        {
            "question": "What is money?",
            "options": ["Something people use to buy things", "A type of food", "A game", "A toy"],
            "answer": "Something people use to buy things",
            "explanation": "Money is commonly used to pay for goods and services."
        },
        {
            "question": "If you have $10 and spend $3, how much is left?",
            "options": ["$5","$6", "$7","$8"],
            "answer": "$7",
            "explanation": "$10 minus $3 equals $7."
        },
        {
            "question": "What does 'spend' mean?",
            "options": ["Use money to buy something", "Save money", "Find money", "Count toys"],
            "answer": "Use money to buy something",
            "explanation": "Spending means using money to purchase something."
        },
        {
            "question": "Which is usually a want?",
            "options": ["Water", "Food", "A place to sleep", "A new toy"],
            "answer": "A new toy",
            "explanation": "A toy can be fun to have, but it is not normally necessary for basic living."
        },
        {
            "question": "Where can you keep money safely?",
            "options": ["A savings account", "On the sidewalk", "In the middle of a road", "In a puddle"],
            "answer": "A savings account",
            "explanation": "A savings account is designed to help people safely store money."
        },
        {
            "question": "What should you do before buying something?",
            "options": ["Think about whether you need it", "Buy it immediately", "Throw away your money", "Ignore the price"],
            "answer": "Think about whether you need it",
            "explanation": "Thinking before buying can help you make smart money choices."
        },
        {
            "question": "If something costs $5, what do you need to buy it?",
            "options": ["At least $5", "Exactly $1", "Nothing", "Only a toy"],
            "answer": "At least $5",
            "explanation": "You need at least $5 to pay for something that costs $5."
        },
        {
            "question": "What does it mean to earn money?",
            "options": ["Get money for work or a service", "Lose money", "Throw money away", "Hide money"],
            "answer": "Get money for work or a service",
            "explanation": "People can earn money by working or providing useful goods and services."
        },
        {
            "question": "Which choice is a smart way to use money?",
            "options": ["Save some money", "Spend everything immediately", "Lose your money", "Buy everything you see"],
            "answer": "Save some money",
            "explanation": "Saving some money can help you prepare for future needs and goals."
        }
    ],

    2: [
        {
            "question": "What is a 'Budget'?",
            "options": [
                "A plan for how to use your money",
                "A secret password",
                "A type of luggage",
                "A math test"
            ],
            "answer": "A plan for how to use your money",
            "explanation": "A budget helps you plan how much money you receive, spend, and save."
        },
        {
            "question": "If you earn $20 and spend $12, how much can you save?",
            "options": ["$6","$8", "$10","$12"],
            "answer": "$8",
            "explanation": "$20 minus $12 equals $8."
        },
        {
            "question": "Why do people make budgets?",
            "options": ["To plan how to use money", "To lose money", "To avoid counting money", "To spend without thinking"],
            "answer": "To plan how to use money",
            "explanation": "A budget helps you decide how much money to spend, save, and possibly give."
        },
        {
            "question": "What is income?",
            "options": ["Money you receive", "Money you lose", "A shopping list", "A type of bank"],
            "answer": "Money you receive",
            "explanation": "Income is money that comes in, such as money earned from work."
        },
        {
            "question": "What is an expense?",
            "options": ["Money you spend", "Money you save", "Money you find", "Money you earn"],
            "answer": "Money you spend",
            "explanation": "An expense is money that you pay for goods, services, or other costs."
        },
        {
            "question": "You have $30 and want to buy something for $18. How much will you have left?",
            "options": ["$10","$12", "$14","$16"],
            "answer": "$12",
            "explanation": "$30 minus $18 equals $12."
        },
        {
            "question": "Which is an example of an expense?",
            "options": ["Paying for groceries", "Receiving a paycheck", "Saving money", "Getting a gift"],
            "answer": "Paying for groceries",
            "explanation": "Buying groceries requires you to spend money, so it is an expense."
        },
        {
            "question": "What should you do if you want to buy something expensive?",
            "options": ["Save for it", "Spend all your money", "Ignore the price", "Borrow without thinking"],
            "answer": "Save for it",
            "explanation": "Saving over time can help you afford expensive purchases without spending all your money at once."
        },
        {
            "question": "What is a savings goal?",
            "options": ["Something you plan to save money for", "A way to lose money", "A shopping receipt", "A type of tax"],
            "answer": "Something you plan to save money for",
            "explanation": "A savings goal gives you a specific reason to set money aside."
        },
        {
            "question": "If you save $5 each week for 4 weeks, how much will you save?",
            "options": ["$10","$15", "$20","$25"],
            "answer": "$20",
            "explanation": "$5 multiplied by 4 weeks equals $20."
        },
        {
            "question": "Which choice can help you stay within a budget?",
            "options": ["Track your spending", "Ignore your spending", "Buy everything you want", "Never check prices"],
            "answer": "Track your spending",
            "explanation": "Tracking spending helps you see where your money is going."
        },
        {
            "question": "What is a financial goal?",
            "options": ["A money target you want to reach", "A type of toy", "A shopping cart", "A bank building"],
            "answer": "A money target you want to reach",
            "explanation": "A financial goal is something you want to accomplish with your money."
        },
        {
            "question": "If you have $50 and spend $25, what fraction of your money did you spend?",
            "options": ["One quarter", "One half", "Three quarters", "All of it"],
            "answer": "One half",
            "explanation": "$25 is half of $50."
        },
        {
            "question": "Which is a good budgeting habit?",
            "options": ["Plan before spending", "Spend without checking", "Ignore your bills", "Use all your savings"],
            "answer": "Plan before spending",
            "explanation": "Planning ahead helps you make sure your money covers important needs and goals."
        },
        {
            "question": "Why might someone compare prices before buying something?",
            "options": ["To find a better deal", "To spend more money", "To lose money", "To avoid shopping"],
            "answer": "To find a better deal",
            "explanation": "Comparing prices can help you find the best value for your money."
        }
    ],

    3: [
        {
            "question": "What is an 'Investment'?",
            "options": [
                "Money put into something with the goal of earning more money",
                "Money you must spend immediately",
                "A type of bank password",
                "Money that can never lose value"
            ],
            "answer": "Money put into something with the goal of earning more money",
            "explanation": "An investment is something you put money into hoping it will grow in value or earn income, but investments can also lose value."
        },
        {
            "question": "What can interest do to savings?",
            "options": ["Help it grow", "Makes it vanish", "Keeps it the same", "Turns it into debt"],
            "answer": "Help it grow",
            "explanation": "Interest can add money to your savings over time."
        },
        {
            "question": "What is the main purpose of an emergency fund?",
            "options": ["Pay for unexpected expenses", "Buy toys every day", "Spend money quickly", "Avoid saving"],
            "answer": "Pay for unexpected expenses",
            "explanation": "An emergency fund provides money for unexpected costs."
        },
        {
            "question": "What is a financial risk?",
            "options": ["The possibility of losing money", "A guaranteed profit", "A savings goal", "A budget"],
            "answer": "The possibility of losing money",
            "explanation": "Financial risk is the possibility that you could lose some or all of your money."
        },
        {
            "question": "Why might people diversify their investments?",
            "options": ["To spread out risk", "To guarantee profit", "To spend everything", "To avoid saving"],
            "answer": "To spread out risk",
            "explanation": "Diversification means spreading money among different investments instead of relying on only one."
        },
        {
            "question": "What is the main difference between a debit card and cash?",
            "options": ["A debit card takes money directly from your bank account", "A debit card is free money", "A debit card creates a loan", "There is no difference"],
            "answer": "A debit card takes money directly from your bank account",
            "explanation": "Debit cards spend money that is already in your bank account."
        },
        {
            "question": "What is a bank deposit?",
            "options": ["Putting money into your bank account", "Taking money out of a bank", "Borrowing a car from a bank", "Paying a store cash"],
            "answer": "Putting money into your bank account",
            "explanation": "A deposit means placing money into your bank account for safekeeping or saving."
        },
        {
            "question": "What is borrowing money called?",
            "options": ["Taking a loan", "Saving", "Earning", "Investing"],
            "answer": "Taking a loan",
            "explanation": "A loan is money borrowed with an agreement to repay it."
        },
        {
            "question": "What does a borrower usually have to do with a loan?",
            "options": ["Repay it", "Destroy it", "Give it away", "Forget about it"],
            "answer": "Repay it",
            "explanation": "Borrowed money generally must be repaid according to the loan agreement."
        },
        {
            "question": "Why is starting to save early helpful?",
            "options": ["Money has more time to grow", "You never need a budget", "You can avoid all expenses", "You automatically become rich"],
            "answer": "Money has more time to grow",
            "explanation": "Starting early gives savings and investments more time to potentially grow."
        },
        {
            "question": "What is a return on investment?",
            "options": ["The gain or loss from an investment", "A shopping receipt", "A bank password", "A monthly bill"],
            "answer": "The gain or loss from an investment",
            "explanation": "Return measures how an investment performs, including gains or losses."
        },
        {
            "question": "Which investment generally has higher risk?",
            "options": ["An investment with large price changes", "Cash kept in a wallet", "A fixed savings amount", "A guaranteed payment"],
            "answer": "An investment with large price changes",
            "explanation": "Large price changes can mean a greater possibility of losing money."
        },
        {
            "question": "What is inflation?",
            "options": ["A general rise in prices", "A type of savings account", "A way to earn a paycheck", "A loan payment"],
            "answer": "A general rise in prices",
            "explanation": "Inflation means prices generally increase over time, reducing what the same amount of money can buy."
        },
        {
            "question": "What does purchasing power mean?",
            "options": ["How much you can buy with your money", "How much money you earn", "How many banks exist", "How many investments you own"],
            "answer": "How much you can buy with your money",
            "explanation": "Purchasing power describes the amount of goods and services your money can buy."
        },
        {
            "question": "What is a good reason to research an investment before buying it?",
            "options": ["To understand its risks and potential", "To guarantee a profit", "To avoid learning about it", "To spend money faster"],
            "answer": "To understand its risks and potential",
            "explanation": "Research can help you understand how an investment works and what risks it may have."
        }
    ],

    4: [
        {
            "question": "If a board game costs $20 and sales tax is 5%, what is the final cost?",
            "options": ["$20.50", "$21.00", "$22.00", "$25.00"],
            "answer": "$21.00",
            "explanation": "5% of $20 is $1.00 in tax, bringing the total to $21.00."
        },
        {
            "question": "A pair of shoes is originally $40 and is on sale for 25% off. How much do you save?",
            "options": ["$5", "$10", "$15", "$20"],
            "answer": "$10",
            "explanation": "25% of $40 (one quarter of 40) is $10."
        },
        {
            "question": "Store A sells 2 notebooks for $6. Store B sells 4 notebooks for $10. Which is the better deal per notebook?",
            "options": ["Store B ($2.50 each)", "Store A ($3.00 each)", "They cost the same", "Store A ($2.00 each)"],
            "answer": "Store B ($2.50 each)",
            "explanation": "Store A is $3.00 per notebook ($6 / 2), while Store B is $2.50 each ($10 / 4)."
        },
        {
            "question": "How does using a credit card differ from using a debit card?",
            "options": ["Credit cards borrow money that must be paid back later", "Debit cards borrow money from a store", "Credit cards only use cash in your wallet", "They work exactly the same way"],
            "answer": "Credit cards borrow money that must be paid back later",
            "explanation": "Credit cards let you borrow money up to a limit, while debit cards use money already in your account."
        },
        {
            "question": "What is the difference between a fixed expense and a variable expense?",
            "options": [
                "Fixed expenses usually stay similar, while variable expenses can change",
                "Fixed expenses are always free",
                "Variable expenses can never change",
                "There is no difference"
            ],
            "answer": "Fixed expenses usually stay similar, while variable expenses can change",
            "explanation": "Fixed expenses tend to stay consistent, while variable expenses can change from one period to another."
        },
        {
            "question": "What is an opportunity cost?",
            "options": [
                "What you give up when choosing one option",
                "Free money from a bank",
                "A type of investment",
                "Money you find"
            ],
            "answer": "What you give up when choosing one option",
            "explanation": "An opportunity cost is the value of the next-best choice you give up."
        },
        {
            "question": "In the popular '50/30/20' budget rule, what does the 20% usually stand for?",
            "options": ["Savings and debt repayment", "Wants and entertainment", "Needs and bills", "Taxes only"],
            "answer": "Savings and debt repayment",
            "explanation": "The 50/30/20 framework suggests 50% for needs, 30% for wants, and 20% for savings/debt."
        },
        {
            "question": "What happens when you pay only the minimum on some credit card balances?",
            "options": [
                "It can take longer to repay the balance and cost more interest",
                "The balance disappears",
                "You automatically earn money",
                "The purchase becomes free"
            ],
            "answer": "It can take longer to repay the balance and cost more interest",
            "explanation": "Paying only the minimum can extend repayment and increase the total interest paid."
        },
        {
            "question": "Why should you compare the total cost of a loan?",
            "options": [
                "To understand what you will actually pay",
                "To make the loan longer",
                "To avoid reading the agreement",
                "To guarantee approval"
            ],
            "answer": "To understand what you will actually pay",
            "explanation": "Looking at the total cost helps you understand interest and fees in addition to the amount borrowed."
        },
        {
            "question": "What is a financial trade-off?",
            "options": [
                "Choosing one financial option instead of another",
                "Getting something for free",
                "Avoiding every expense",
                "Earning money without working"
            ],
            "answer": "Choosing one financial option instead of another",
            "explanation": "A trade-off happens when choosing one option means giving up another option."
        },
        {
            "question": "What can happen if prices rise faster than your savings grow?",
            "options": [
                "Your money may buy less",
                "Your money automatically doubles",
                "Your expenses disappear",
                "Your savings become debt"
            ],
            "answer": "Your money may buy less",
            "explanation": "When prices rise, the purchasing power of money can decrease."
        },
        {
            "question": "Why might someone use automatic savings transfers?",
            "options": [
                "To save consistently",
                "To spend more accidentally",
                "To avoid having a bank account",
                "To increase their bills"
            ],
            "answer": "To save consistently",
            "explanation": "Automatic transfers can make saving a regular habit."
        },
        {
            "question": "What is 'delayed gratification' in personal finance?",
            "options": ["Waiting to buy something now so you can achieve a bigger goal later", "Spending money right away", "Forgetting how much money you have", "Returning an item to the store"],
            "answer": "Waiting to buy something now so you can achieve a bigger goal later",
            "explanation": "Delayed gratification means resisting an immediate impulse purchase in favor of a larger future reward."
        },
        {
            "question": "What should you consider before taking a loan?",
            "options": [
                "Interest, fees, and whether you can afford the payments",
                "Only the color of the bank",
                "Only how quickly you receive the money",
                "Nothing"
            ],
            "answer": "Interest, fees, and whether you can afford the payments",
            "explanation": "Understanding the full cost and whether payments fit your budget is important before borrowing."
        },
        {
            "question": "Why is setting a specific savings goal useful?",
            "options": [
                "It gives you a clear target",
                "It makes saving impossible",
                "It guarantees investment profits",
                "It eliminates all expenses"
            ],
            "answer": "It gives you a clear target",
            "explanation": "A specific goal makes it easier to know how much you need to save and track your progress."
        }
    ],

    5: [
        {
            "question": "You deposit $1,000 into an account earning 5% interest compounded annually. After one year, you have $1,050. Approximately how much will you have after the second year?",
            "options": ["$1,100.00", "$1,102.50", "$1,150.00", "$1,052.50"],
            "answer": "$1,102.50",
            "explanation": "In the second year, you earn 5% interest on $1,050, not just the original $1,000. 5% of $1,050 is $52.50, bringing the total to $1,102.50."
        },
        {
            "question": "According to the 'Rule of 72', approximately how many years will it take for an investment to double at a fixed annual return of 6%?",
            "options": ["6 years", "12 years", "18 years", "72 years"],
            "answer": "12 years",
            "explanation": "Divide 72 by the annual rate of return: 72 / 6 = 12 years."
        },
        {
            "question": "What is diversification mainly intended to do?",
            "options": [
                "Reduce the impact of one investment performing poorly",
                "Guarantee that every investment makes money",
                "Eliminate all financial risk",
                "Make taxes disappear"
            ],
            "answer": "Reduce the impact of one investment performing poorly",
            "explanation": "Diversification spreads risk so that one poor-performing asset does not derail the entire portfolio."
        },
        {
            "question": "Two people apply for the same loan. One has a strong credit history, while the other frequently missed payments. Why might the first person receive a lower interest rate?",
            "options": [
                "Their repayment history indicates lower lending risk",
                "They automatically have a higher income",
                "They are legally exempt from paying interest",
                "A credit score reflects total bank account balance"
            ],
            "answer": "Their repayment history indicates lower lending risk",
            "explanation": "Lenders evaluate risk via credit profiles; lower risk that the loan will not be repaid often results in more favorable borrowing terms."
        },
        {
            "question": "You borrow $4,000 for a car and repay a total of $4,600 over the life of the loan. What was the principal?",
            "options": [
                "$4,000",
                "$600",
                "$4,600",
                "$8,600"
            ],
            "answer": "$4,000",
            "explanation": "The principal is the original amount borrowed, which is $4,000. The additional $600 represents the cost of borrowing."
        },
        {
            "question": "Why does extending a loan term from 3 years to 6 years usually increase the overall cost, even if monthly payments drop?",
            "options": [
                "You pay interest over a longer duration",
                "The principal automatically increases each month",
                "Longer loans carry zero interest rates",
                "Sales tax is applied every year"
            ],
            "answer": "You pay interest over a longer duration",
            "explanation": "While lower monthly payments improve short-term cash flow, paying interest across more months increases total borrowing costs."
        },
        {
            "question": "You keep $1,000 in cash in a drawer. Over 5 years, inflation averages 3% per year. What happens to the purchasing power of that cash?",
            "options": [
                "It decreases because goods and services cost more",
                "It increases because the bills are older",
                "It remains identical because you still possess $1,000",
                "It doubles automatically"
            ],
            "answer": "It decreases because goods and services cost more",
            "explanation": "Inflation reduces real purchasing power over time if money does not earn a return matching or exceeding the inflation rate."
        },
        {
            "question": "You invest $200 and later sell the asset for $230. What is your percentage return?",
            "options": ["10%", "15%", "20%", "30%"],
            "answer": "15%",
            "explanation": "The dollar gain is $30 ($230 - $200). $30 / $200 = 0.15, or a 15% return."
        },
        {
            "question": "You have $4,000 in savings, $2,000 in investments, and owe $1,500 on a credit balance. What is your net worth?",
            "options": ["$4,500", "$6,000", "$2,500", "$7,500"],
            "answer": "$4,500",
            "explanation": "Net worth equals total assets ($4,000 + $2,000 = $6,000) minus total liabilities ($1,500), which equals $4,500."
        },
        {
            "question": "You invest $1,000 and it yields an 8% gain. What is the total value of your investment?",
            "options": ["$1,008", "$1,080", "$1,800", "$920"],
            "answer": "$1,080",
            "explanation": "8% of $1,000 is $80 ($1,000 * 0.08). Adding this to principal yields $1,080."
        },
        {
            "question": "Two loans are both for $5,000. Loan A has a lower interest rate with a 5-year term; Loan B has a higher interest rate with a 2-year term. What should you compare to determine which loan is cheaper overall?",
            "options": [
                "The total amount repaid over the life of the loan",
                "Only the upfront document fee",
                "The lowest monthly payment amount",
                "How fast the application is approved"
            ],
            "answer": "The total amount repaid over the life of the loan",
            "explanation": "Comparing the total amount repaid, including interest and fees, gives a clearer picture of which loan costs less overall."
        },
        {
            "question": "Why is high-interest consumer debt typically prioritized in a debt repayment plan?",
            "options": [
                "Higher interest rates can make the debt cost more over time.",
                "Paying high-interest debt first is legally mandatory",
                "It automatically improves your salary",
                "High-interest loans cannot be paid off early"
            ],
            "answer": "Higher interest rates can make the debt cost more over time.",
            "explanation": "The higher the interest rate, the more interest you may pay while carrying a balance, so paying high-interest debt sooner can reduce borrowing costs"
        },
        {
            "question": "What is the main difference between owning a stock and owning a bond?",
            "options": [
                "A stock represents ownership in a company; a bond represents money lent to a company or government",
                "A stock guarantees regular payments; a bond gives you ownership in a company",
                "Stocks are risk-free; bonds always lose money",
                "Stocks cannot be bought or sold"
            ],
            "answer": "A stock represents ownership in a company; a bond represents money lent to a company or government",
            "explanation": "Buying a stock gives you partial ownership in a company. Buying a bond means lending money to a company or government in exchange for promised repayment."
        },
        {
            "question": "What does 'liquidity' refer to in personal finance?",
            "options": [
                "How quickly an asset can be converted to cash with minimal loss of value",
                "The total cash balance held by central banks",
                "The proportion of monthly income lost to income taxes",
                "A loan structure with adjustable interest rates"
            ],
            "answer": "How quickly an asset can be converted to cash with minimal loss of value",
            "explanation": "Cash and savings accounts represent high liquidity, whereas physical assets like real estate take longer to liquidate."
        },
        {
            "question": "Why is an emergency fund typically kept in a high-yield savings account rather than stocks or real estate?",
            "options": [
                "It prioritizes keeping the money safe and immediate liquidity over high risk",
                "Savings accounts are legally required for emergency funds",
                "Stocks cannot be sold during emergencies",
                "Savings accounts offer the highest historical long-term returns"
            ],
            "answer": "It prioritizes keeping the money safe and immediate liquidity over high risk",
            "explanation": "Emergency funds must remain stable and liquid so cash can be accessed immediately without market volatility risk."
        }
    ]
}


    
    client = get_gemini_client()
    difficulty_map = {
        1: "easy, beginner finance question, multiple choice, simple math for 5 year olds",
        2: "medium difficulty, some calculations, basic financial concepts, 7 year olds",
        3: "harder, involves reasoning and multi-step finance problems, suitable for 9 year olds",
        4: "advanced, challenging finance problem suitable for children who mastered levels 1-3, suiltable for 11 year olds",
        5: "expert kid-friendly finance problem, multi-step reasoning, real-world scenario, suitable for 12 year olds"
    }
    system_instruction = (
            "You are a friendly financial literacy teacher for kids. "
            "Your tone is encouraging and simple. Always output valid JSON using this schema:"
            "{'question': str, 'options': [str], 'answer': str, 'explanation': str}"
        )
    # Use a safe lookup for difficulty description to avoid KeyError for unexpected levels
    difficulty_desc = difficulty_map.get(level, difficulty_map.get(3))

    prompt = (
        f"Generate one multiple-choice finance question for level {level} ({difficulty_desc}) for children. "
        "Make sure it's appropriate for KIDS age 3-7 and keep the question under 130 characters."
    )

    try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", #gemini-3-flash-preview, gemini-flash-latest
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON
            data = json.loads(response.text)
            
            # 2. Validate against the Schema immediately!
            # This ensures if Gemini hallucinates a wrong field, we catch it here.
            return QuestionSchema(**data)

    except Exception as e:
        # Fallback or retry logic could go here
        print(f"!!! FALLBACK ACTIVATED: {e}")
        # Provide fallback pools for higher levels if missing
        level_pool = fallback_questions.get(level)
        if not level_pool:
            level_pool = fallback_questions.get(1)
        fallback_data = random.choice(level_pool)
        # Return a default error question or re-raise
        return QuestionSchema(**fallback_data)