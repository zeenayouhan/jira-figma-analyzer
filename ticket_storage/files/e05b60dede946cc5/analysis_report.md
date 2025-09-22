# [FE] Implement a pre-session survey for the investment session (MANUAL-001)

## Ticket Information
- **Priority**: Medium
- **Assignee**: Unassigned
- **Reporter**: You
- **Created**: 2025-09-11T23:43:08.133048
- **Labels**: 
- **Components**: 

## Description
Implement the pre-session survey flow for the investment session in the app. The survey will guide users through a set of questions to capture their financial goals and investment preferences before their advisory session. 



The flow includes

Updated session booking confirmation screen or updated session screen in the pre-survey state on the advisor tab

Multiple question screens (single and multiple-choice)

Confirmation screen after completion

Updated session screen in the post-survey state on the advisor tab



Design

Please check the design on the prototype mode to check the detailed flow and behavior



ACs

Session Booking Confirmation Screen

New design:

Confirmation details visible

Given the user is on the Session Booking Confirmation screen for the investment session

When the screen is displayed

Then the updated design shows the CTA to the investment survey along with the new description.

Survey entry point shown

Given the user is on the Session Booking Confirmation screen for the investment session

When they tap the CTA to the survey

Then the app navigates the user to the first survey question screen

Answer survey later button

Given the user is on the Session Booking Confirmation screen for the investment session

When the screen is displayed

Then the screen shows an “Answer survey later” button which navigates the user to the Session Home Screen on the Advisor Tab

Session Home Screen on the Advisor Tab

New designs: 

Survey not started yet (Pre-survey state)

Given the user is on the Session Home Screen on the Advisor Tab before completing the survey

When the screen is displayed

Then the updated design highlights that the survey has not been completed and provides a new title, description, and CTA to begin the survey.

Survey completion acknowledged without CTA (Post-survey state)

Given the user is on the Session Home Screen on the Advisor Tab after submitting the survey

When the screen is displayed

Then the updated design shows the survey as completed with a confirmation message.

And  there is no CTA to start the survey, and the UI instead shows the completed status.

Question Screens – Core Behavior

All questions are multiple-choice and required

CTA button state

Given the user is on any question screen

When no answer is selected

Then the “次へ” button remains inactive until an answer is selected.

CTA button active state

Given the user is on any question screen with at least one valid selection (or valid free-text entry when “その他” is chosen)

When the screen is displayed

Then the “次へ” button becomes active and tappable.

Free-text input (その他 option)

Given the user is on a question screen with a “その他” (Other) option

When they select the “その他” option

Then a free-text field appears for input.

Free-text input validation

Given the user has selected the “その他” option

When no text is entered in the free-text field

Then the “次へ” button remains inactive until text is filled.

Progress indicator

Given the user is on any question screen

When the screen renders

Then a progress indicator shows the current step out of total steps.

Progress indicator animation

Given the user moves to the next question

When the progress indicator updates

Then a glitter animation plays as implemented in the LP pre-session survey.

Close button tapped – confirmation popup

Given the user is on any question screen

When they tap the close (✕) button

Then the app shows the confirmation popup “このままページを閉じてもよろしいですか？” as implemented on the post-session survey by Rishan.

Discard confirmation – stay on page

Given the confirmation popup is shown

When the user taps “記入に戻る” (Return to editing)

Then the popup closes and the user remains on the same question screen with answers intact.

Discard confirmation – exit survey

Given the confirmation popup is shown

When the user taps “保存せずに閉じる” (Close without saving)

Then the survey closes and all answers are discarded.

Back navigation within survey

Given the user is on any question screen except the first

When they tap the back arrow

Then the previous question loads with their prior selections restored.

No auto-save or resume function

Given the user exits the survey before completion

When they reopen it later

Then no answers are restored and the survey restarts from the beginning.

Completion & Handoff

Completion screen

Given the user has answered the final question

When they tap “アンケートを提出する”

Then a Survey Complete screen appears confirming submission.

Return to advisory session

Given the user is on the Survey Complete screen

When they tap the CTA button “閉じる”

Then the app returns to the advisory session screen and marks the pre-session survey as completed for that session.

Errors, Localization, Accessibility, Analytics

Network error while submitting

Given the user is on the final question and taps “アンケートを提出する”

When submission fails due to a network error

Then the app displays an error screen: https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=144252-153026&t=w5U3lTdHqW5T6fgg-11



Figma Links:
https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=142436-171179&p=f&t=PaRBcKHht9mVbzNC-0

## Figma Links
- https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=142436-171179&p=f&t=PaRBcKHht9mVbzNC-0
- https://www.figma.com/design/fnCxddHpd5tOcjYxzliAxc/Habitto-App-UI--Sprint-Execution?node-id=144252-153026&t=w5U3lTdHqW5T6fgg-11

## Analysis Results

### Suggested Questions (12)
- What is the backend infrastructure required to store and manage the survey responses securely?
- How will the app handle interruptions or app closures during the survey process to ensure data integrity and user experience?
- Are there any specific accessibility considerations for users with disabilities when interacting with the survey screens?
- How will the survey data be integrated with existing analytics tools to track user responses and behavior?
- What measures are in place to handle potential localization requirements for the survey questions and answers?
- How will the app handle scenarios where a user tries to manipulate or bypass the survey flow?
- What is the strategy for ensuring data privacy and compliance with regulations when collecting user data through the survey?
- Will there be any backend API endpoints required to support the survey functionality, such as saving responses or fetching survey questions dynamically?
- How will the app handle cases where a user navigates away from the survey screens and then tries to resume the survey at a later time?
- Are there any specific performance considerations to optimize the loading and rendering of the survey screens, especially on mobile devices?
- How will the completion of the pre-session survey be communicated to the advisor or integrated into the overall session management system?
- What error handling mechanisms are in place to inform users in case of server-side errors or issues with submitting the survey responses?

### Design Questions (12)
- How is the "CTA to the investment survey" visually differentiated on the Session Booking Confirmation Screen to guide users to start the pre-session survey flow?
- In the pre-survey state on the Advisor Tab, how does the updated design indicate that the survey has not been completed yet? Are there specific visual cues for this state?
- Can you describe the visual hierarchy and placement of the "Answer survey later" button on the Session Booking Confirmation Screen for users who choose to skip the survey initially?
- How is the progress indicator designed to show the current step out of total steps on the question screens to guide users through completing the survey?
- Regarding the free-text input field for the "その他" option, how is the transition between selecting the option and the appearance of the input field handled to maintain a seamless user experience?
- Are there specific error states designed for scenarios like network errors while submitting the survey? How are these errors visually communicated to users?
- How is the completion screen designed to confirm submission of the survey, and is there any visual feedback provided to users upon successful submission?
- Considering accessibility, how is the contrast ratio maintained for the active and inactive states of the "次へ" button on the question screens to ensure visibility for all users?
- Are there specific animations or micro-interactions implemented to enhance the user experience, such as the glitter animation for the progress indicator mentioned in the requirements?
- How is the transition back to the advisory session screen designed after completing the survey to ensure a smooth handoff for users?
- What accessibility standards need to be met for this design?
- How should the design adapt to different mobile screen sizes?

### Business Questions (15)
- How will the implementation of a pre-session survey impact the platform's revenue by potentially identifying new opportunities for tailored investment products or services?
- What strategies can be put in place to leverage the data collected from the pre-session survey to enhance client acquisition and retention rates?
- How will the pre-session survey contribute to improving advisor productivity and efficiency by providing them with relevant client information upfront?
- What compliance and regulatory considerations need to be addressed when implementing a pre-session survey feature to ensure data privacy and security?
- What risks are associated with the pre-session survey feature, and how can they be effectively managed to mitigate any negative impacts on the platform?
- How will the introduction of a pre-session survey differentiate our platform from competitors and enhance our market positioning within the financial advisory industry?
- What scalability challenges may arise from implementing the pre-session survey feature, and how can they be effectively addressed to support operational growth?
- What resources, both in terms of technology and personnel, will be required to implement and maintain the pre-session survey feature, and what is the expected return on investment?
- How will the integration of the pre-session survey feature with existing appointment management processes streamline workflows and enhance overall business efficiency?
- What key success metrics should be established to measure the effectiveness of the pre-session survey feature in improving client relationships and driving business growth?
- How can the data collected from the pre-session survey be leveraged to tailor personalized investment recommendations and enhance the overall client experience?
- In what ways can the pre-session survey feature be optimized to ensure accessibility for all users, including those with disabilities or language barriers?
- How can analytics and data insights derived from the pre-session survey be used to identify trends, preferences, and opportunities for product innovation and service enhancements?
- What steps need to be taken to ensure that the pre-session survey feature aligns with industry best practices and standards for data collection and privacy protection?
- How can the pre-session survey feature be utilized to proactively address client needs and preferences, ultimately leading to increased client satisfaction and loyalty?

### Technical Considerations (6)
- Performance testing and optimization needed
- Caching strategy should be evaluated
- React Native platform-specific implementations
- App store deployment considerations
- High complexity design (Habitto App UI: Sprint Execution) may require additional development time
- High complexity design (Habitto App UI: Sprint Execution) may require additional development time

### Test Cases (25)
- **Functional Tests:**
- 1. Test the core feature functionality by navigating through the pre-session survey flow, answering all questions, and submitting the survey successfully.
- - Objective: Validate that users can complete the pre-session survey as intended.
- - Expected Outcome: The survey is completed, and the user receives a confirmation of submission.
- 2. Test the user workflow by attempting to skip questions or navigate out of the survey midway.
- - Objective: Ensure that users are guided through the entire survey without the ability to skip questions or exit prematurely.
- - Expected Outcome: Users are prevented from skipping questions or exiting the survey before completion.
- 3. Test the integration with existing financial advisory features by booking an investment session and starting the pre-session survey flow.
- - Objective: Verify that the pre-session survey seamlessly integrates with the investment session booking process.
- - Expected Outcome: Users can access the survey from the session booking confirmation screen and vice versa.
- 4. Test the business rule validation by providing invalid or incomplete answers in the survey.
- - Objective: Validate that the system enforces business rules related to required fields and answer formats.
- - Expected Outcome: Users are prompted to provide valid answers before proceeding to the next question.
- **Security & Compliance Tests:**
- 5. Test data protection and privacy by reviewing the data handling practices during the survey submission process.
- - Objective: Ensure that user data is securely stored and transmitted according to privacy regulations.
- - Expected Outcome: User data is encrypted and protected from unauthorized access.
- 6. Test financial services compliance requirements by verifying that the survey does not request sensitive financial information.
- - Objective: Confirm that the survey adheres to financial regulations by not collecting sensitive data.
- - Expected Outcome: No requests for confidential financial information are present in the survey.
- 7. Test user authentication and authorization by accessing the survey from different user roles (e.g., advisor, client).
- - Objective: Validate that only authorized users can access and complete the pre-session survey.
- - Expected Outcome: Unauthorized users are restricted from participating in the survey.
- 8. Test audit trail and logging by tracking user interactions and submissions within the survey.
- - Objective: Ensure that a comprehensive audit trail is maintained for all survey activities.

### Risk Areas (5)
- Very complex design (Habitto App UI: Sprint Execution) may exceed estimated effort
- Very complex design (Habitto App UI: Sprint Execution) may exceed estimated effort
- Performance requirements may need additional optimization time
- Cross-platform compatibility testing required
- App store approval process may add timeline risk

---
*Analysis generated on 2025-09-11T23:43:08.133048 (Version 1.0)*
