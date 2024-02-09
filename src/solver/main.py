from .agent import Agent


def main():
    player1_agent, player2_agent = Agent.new_agents()
    print()
    print(player1_agent)
    print()
    print(player2_agent)
