package = "onearth_gc_gts"
version = "0.1-1"
source = {
   url = "..." -- We don't have one yet
}
description = {
   summary = "Lua utilties for use with the OnEarth Apache modules",
   detailed = [[
      Description here
   ]],
   homepage = "http://...", -- We don't have one yet
   license = "MIT"
}
dependencies = {
   "lua >= 5.1",
   "luafilesystem",
   "lua-yaml",
   "luasocket",
   "json-lua",
   "http",
   "argparse",
   "penlight",
   "luaossl",
   "md5"
}
build = {
   type = "builtin",
   modules = {
      ["onearth_gc_gts"] = "gc_service.lua"
   }
}