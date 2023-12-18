from typing import Any

from app.agents.base import AgentBase
from app.utils.prisma import prisma


class WorkflowBase:
    def __init__(
        self, workflow: Workflow, workflowSteps: any, session_id: str, enable_streaming: bool = False
    ):
        self.workflow = workflow
        self.enable_streaming = enable_streaming
        self.workflowSteps = workflowSteps
        self.session_id = session_id

    async def arun(self, input: Any):
        self.workflow.steps.sort(key=lambda x: x.order)
        previous_output = input
        steps_output = {}
        stepIndex = 0

        for step in self.workflow.steps:
            agent = await AgentBase(
                agent_id=step.agentId,
                session_id=self.session_id,
                enable_streaming=True,
                callback=self.workflowSteps[stepIndex]['callback'],
            ).get_agent()

            task = asyncio.ensure_future(
                agent.acall(
                    inputs={"input": previous_output},
                )
            )

            await task
            agent_response = task.result()
            previous_output = agent_response.get("output")
            steps_output[step.order] = agent_response
        return {"steps": steps_output, "output": previous_output}
