import asyncio
import logging

# Configure logging for the game client
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from game import Game


async def main():
    game = Game()
    await game.run()


asyncio.run(main())
