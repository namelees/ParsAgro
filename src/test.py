import asyncio
from Infra.groups import load_groups_data, find_group, get_groups_database
from Infra.sheedule import parse_schedule_with_containers

print("hello")

load_groups_data();

async def async_test():
    group = find_group("24ф-д-9-3");
    schedule = await parse_schedule_with_containers(group[0][1]);
    print("schedule: ", schedule);


asyncio.run(async_test());

print("ok")
