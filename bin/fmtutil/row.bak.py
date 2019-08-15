    class fmtd: pass
    knoco0cls = type(f'{knoco0}', (), {})
    knoco1cls = type(f'{knoco1}', (), {})
    noco0cls = type('noco0cls',(),{knoco0:vnoco0})
    co0cls = type('co0cls',(),{knoco0:vco0})
    noco1cls = type('noco1cls',(),{knoco1:vnoco1})
    co1cls = type('co1cls',(),{knoco1:vco1})
    setattr(fmtd,f'{knoco0}',knoco0cls)
    setattr(fmtd,f'{knoco1}',knoco1cls)
    setattr(knoco0cls,'noco',noco0cls)
    setattr(knoco0cls,'co',co0cls)
    setattr(knoco1cls,'noco',noco1cls)
    setattr(knoco1cls,'co',co1cls)
    knoco0cls, knoco1cls
    noco0cls, co0cls
    noco1cls, co1cls

    convert_key = lambda k: "".join(k.split('_').title())
    class FmtdCellData:
      funcname: str
      args: List[Dict]
    ClsName0 = type(ClsName0 := convert_key(knoco0), (), {})
    ClsName1 = type(ClsName1 := convert_key(knoco1), (), {})
    ClsNoColor = type('NoColor', (), {})
    ClsColor = type('Color', (), {})
    setattr(FmtdCellData,ClsName0,knoco0)
    setattr(FmtdCellData,ClsName1,knoco1)
    setattr(ClsName0,"NoColor",{knoco0:vnoco0})
    setattr(ClsName0,"Color",ClsColor(**{knoco0:vco0}))
    setattr(ClsName1,"NoColor",{knoco1:vnoco1})
    setattr(ClsName1,"Color",{knoco1:vco1})





    noco0cls = type('noco0cls',(),{knoco0:vnoco0})
    co0cls = type('co0cls',(),{knoco0:vco0})
    noco1cls = type('noco1cls',(),{knoco1:vnoco1})
    co1cls = type('co1cls',(),{knoco1:vco1})
    setattr(fmtd,f'{knoco0}',knoco0cls)
    setattr(fmtd,f'{knoco1}',knoco1cls)
    setattr(knoco0cls,'noco',noco0cls)
    setattr(knoco0cls,'co',co0cls)
    setattr(knoco1cls,'noco',noco1cls)
    setattr(knoco1cls,'co',co1cls)
    knoco0cls, knoco1cls
    noco0cls, co0cls



    def noco_factory(noco_dct):
      NoColor = namedtuple('NoColor', list(noco_dct).pop())
      noco = NoColor(**noco_dct)
      return noco
    class co_factory: pass
    setattr(co_factory,'noconco_factory',noconco_factory)
    def co_factory(co_dct):
      Color = namedtuple('Color', list(co_dct).pop())
      co = Color(**co_dct)
      return co
    class noconco_factory: pass
    setattr(noconco_factory,'fmtd',fmtd)
    def noconco_factory(nocod,cod):
      noco = noco_factory(nocod)
      co = co_factory(cod)
      NocoNCo = namedtuple('NocoNCo', list(nocod).pop())
      return NocoNCo

    def fmtd(knoco0,knoco1,kco0,kco1,
      vnoco0,vnoco1,vco0,vco1):
      Fmtd = namedtuple('Fmtd', ", ".join([knoco0,knoco1]))
      fmtd_knoco0 = {knoco0:noconco_factory({knoco0:vnoco0},{knoco0:vco0})}
      fmtd_knoco1 = {knoco1:noconco_factory({knoco1:vnoco1},{knoco1:vco1})}
      fmtd = Fmtd(**fmtd_knoco0,**fmtd_knoco1)
      return fmtd
