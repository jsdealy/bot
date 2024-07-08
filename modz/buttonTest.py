import discord
from discord.ui import Button, View, Select

class Dropdown(Select):
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Option 1', description='This is option 1'),
            discord.SelectOption(label='Option 2', description='This is option 2'),
            discord.SelectOption(label='Option 3', description='This is option 3'),
        ]

        super().__init__(placeholder='Choose an option...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # This function gets called when the user selects an option
        await interaction.response.send_message(f'You selected {self.values[0]}', ephemeral=True)

async def buttonTest(message):
    if message.content.startswith('$hello'):
        list = ["item 1", "item 2"]
        view = View()
        for x in list:
            button = Button(label=x, style=discord.ButtonStyle.primary)
            async def button_callback(interaction):
                await interaction.response.send_message('Button clicked!', ephemeral=True)
            button.callback = button_callback
            view.add_item(button)

        await message.channel.send('Hello!', view=view)
    if message.content.startswith('$menu'):
        # Create the view that holds our dropdown
        view = View()
        view.add_item(Dropdown())

        await message.channel.send('Choose an option from the dropdown:', view=view)

