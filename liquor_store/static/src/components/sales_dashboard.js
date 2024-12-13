/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl
import { browser } from "@web/core/browser/browser"
import { routeToUrl } from "@web/core/browser/router_service"

export class OwlSalesDashboard extends Component {
    // top products
    async getTopProducts() {
        let domain = []; 
        if (this.state.period > 0){
            domain.push(['bottle_ids.selling_date', '>=', this.state.current_date]); 
        }
    
        // Fetch all brands
        const brands = await this.orm.searchRead("liquor_store.brand", domain, ['name']);
    
        // Fetch sold bottle count for each brand and sum them up
        const brandSoldBottleCounts = await Promise.all(brands.map(async (brand) => {
            const bottleIds = await this.orm.search("liquor_store.bottle", [['brand', '=', brand.id], ['status', '=', 'sold']]);
            return {
                brand_name: brand.name,
                sold_bottle_count: bottleIds.length
            };
        }));
    
        // Sort brands by sold bottle count
        brandSoldBottleCounts.sort((a, b) => b.sold_bottle_count - a.sold_bottle_count);
    
        // Take top 5 brands
        const topBrands = brandSoldBottleCounts.slice(0, 5);
    
        const topProducts = {
            data: {
                labels: topBrands.map(brand => brand.brand_name),
                datasets: [
                    {
                        label: 'Sold Bottle Count',
                        data: topBrands.map(brand => brand.sold_bottle_count),
                        hoverOffset: 4,
                    }
                ]
            },
            domain,
            label_field: 'name',
        };
    
        this.state.topProducts = topProducts;
    }  
    
    

    // top sales people
    async getTopSalesPeople(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date','>', this.state.current_date])
        }

        const data = await this.orm.readGroup("sale.report", domain, ['user_id', 'price_total'], ['user_id'], { limit: 5, orderby: "price_total desc" })

        this.state.topSalesPeople = {
            data: {
                labels: data.map(d => d.user_id[1]),
                  datasets: [
                  {
                    label: 'Total',
                    data: data.map(d => d.price_total),
                    hoverOffset: 4,
                  }]
            },
            domain,
            label_field: 'user_id',
        }
    }

    // monthly sales
    async getMonthlySales() {
        const domain = [['selling_date', '>=', this.state.current_date]]; // Filter by selling_date
        const data = await this.orm.readGroup(
            "liquor_store.sales.analysis",
            domain,
            ['selling_date', 'total_sales_amount', 'total_profit'],
            ['selling_date'],
            { orderby: "selling_date", lazy: false }
        );
        console.log("monthly sales", data);
    
        const labels = [...new Set(data.map(d => d.selling_date))];
        const totalSales = data.map(d => d.total_sales_amount);
        const totalProfits = data.map(d => d.total_profit);
    
        this.state.monthlySales = {
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total Sales Amount',
                        data: totalSales,
                        hoverOffset: 4,
                        backgroundColor: "green",
                    },
                    {
                        label: 'Total Profit',
                        data: totalProfits,
                        hoverOffset: 4,
                        backgroundColor: "orange",
                    }
                ]
            },
            domain,
            label_field: 'selling_date',
        };
    }
   
    

    async getTotalProfitPerBrand() {
        let domain = [];
        if (this.state.period > 0) {
            domain.push(['selling_date', '>=', this.state.current_date]);
        }
    
        const data = await this.orm.readGroup("liquor_store.sales.analysis", domain, ['brand_id', 'total_profit'], ['brand_id'], { lazy: false });
        console.log("total profit per brand", data);
    
        const brandProfits = data.map(entry => ({
            brand_id: entry.brand_id[0],
            total_profit: entry.total_profit
        }));
    
        // Fetch brand names corresponding to IDs
        const brandNames = await Promise.all(brandProfits.map(async (entry) => {
            const brand = await this.orm.searchRead("liquor_store.brand", [['id', '=', entry.brand_id]], ['name']);
            return brand[0].name;
        }));
    
        const totalProfitsPerBrand = {
            data: {
                labels: brandNames,
                datasets: [
                    {
                        label: 'Total Profit',
                        data: brandProfits.map(entry => entry.total_profit),
                        hoverOffset: 4,
                        backgroundColor: "purple",
                    }
                ]
            },
            domain,
            label_field: 'name',
        };
    
        this.state.totalProfitPerBrand = totalProfitsPerBrand;
    }
    

    // partner orders
    async getPartnerOrders(){
        let domain = [['state', 'in', ['draft','sent','sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date','>', this.state.current_date])
        }

        const data = await this.orm.readGroup("sale.report", domain, ['partner_id', 'price_total', 'product_uom_qty'], ['partner_id'], { orderby: "partner_id", lazy: false })
        console.log(data)

        this.state.partnerOrders = {
            data: {
                labels: data.map(d => d.partner_id[1]),
                  datasets: [
                  {
                    label: 'Total Amount',
                    data: data.map(d => d.price_total),
                    hoverOffset: 4,
                    backgroundColor: "orange",
                    yAxisID: 'Total',
                    order: 1,
                  },{
                    label: 'Ordered Qty',
                    data: data.map(d => d.product_uom_qty),
                    hoverOffset: 4,
                    //backgroundColor: "blue",
                    type:"line",
                    borderColor: "blue",
                    yAxisID: 'Qty',
                    order: 0,
                }]
            },
            scales: {
                /*Qty: {
                    position: 'right',
                }*/
                yAxes: [
                    { id: 'Qty', position: 'right' },
                    { id: 'Total', position: 'left' },
                ]
            },
            domain,
            label_field: 'partner_id',
        }
    }

    setup(){
        this.state = useState({
            quotations: {
                value:10,
                percentage:6,
            },
            period:90,
        })
        this.orm = useService("orm")
        this.actionService = useService("action")

        const old_chartjs = document.querySelector('script[src="/web/static/lib/Chart/Chart.js"]')
        const router = useService("router")

        if (old_chartjs){
            let { search, hash } = router.current
            search.old_chartjs = old_chartjs != null ? "0":"1"
            hash.action = 86
            browser.location.href = browser.location.origin + routeToUrl(router.current)
        }

        onWillStart(async ()=>{
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.30.1/moment.min.js")
            this.getDates()
            await this.getQuotations()
            await this.getOrders()
            await this.getTotalProfitPerBrand()

            await this.getTopProducts()
            await this.getTopSalesPeople()
            await this.getMonthlySales()
            await this.getPartnerOrders()
        })
    }

    async onChangePeriod(){
        this.getDates()
        await this.getQuotations()
        await this.getOrders()

        await this.getTopProducts()
        await this.getTotalProfitPerBrand()
        await this.getTopSalesPeople()
        await this.getMonthlySales()
        await this.getPartnerOrders()
    }

    getDates(){
        this.state.current_date = moment().subtract(this.state.period, 'days').format('L')
        this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('L')
    }

    async getQuotations(){
        let domain = [['state', 'in', ['quotation_sent', 'quotation']]]; 
        if (this.state.period > 0){
            domain.push(['date', '>', this.state.current_date]); 
        }
        const data = await this.orm.searchCount("liquor_store.sales.order", domain); 
        this.state.quotations.value = data;
    
        // previous period
        let prev_domain = [['state', 'in', ['quotation_sent', 'quotation']]]; 
        if (this.state.period > 0){
            prev_domain.push(['date', '>', this.state.previous_date], ['date', '<=', this.state.current_date]); 
        }
        const prev_data = await this.orm.searchCount("liquor_store.sales.order", prev_domain); 
        const percentage = ((data - prev_data)/prev_data) * 100;
        this.state.quotations.percentage = percentage.toFixed(2);
    }
    

    async getOrders(){
        // orders
        let domain = [['state', 'in', ['sales_order', 'done']]]; 
        if (this.state.period > 0){
            let currentDate = moment(this.state.current_date, 'MM/DD/YYYY').format('YYYY-MM-DD'); 
            domain.push(['date', '>', currentDate]); 
        }
        const data = await this.orm.searchCount("liquor_store.sales.order", domain); 
        //this.state.quotations.value = data

        // previous period
        let prev_domain = [['state', 'in', ['sales_order', 'done']]]; 
        if (this.state.period > 0){
            let previousDate = moment(this.state.previous_date, 'MM/DD/YYYY').format('YYYY-MM-DD');
            let currentDate = moment(this.state.current_date, 'MM/DD/YYYY').format('YYYY-MM-DD'); 
            prev_domain.push(['date', '>', previousDate], ['date', '<=', currentDate]); 
        }
        const prev_data = await this.orm.searchCount("liquor_store.sales.order", prev_domain); 
        const percentage = ((data - prev_data)/prev_data) * 100;

        //revenues
        const current_revenue = await this.orm.readGroup("liquor_store.sales.order", domain, ["total_amount:sum"], [])
        const prev_revenue = await this.orm.readGroup("liquor_store.sales.order", prev_domain, ["total_amount:sum"], [])
        const revenue_percentage = ((current_revenue[0].total_amount - prev_revenue[0].total_amount) / prev_revenue[0].total_amount) * 100

        //average
        const current_average = await this.orm.readGroup("liquor_store.sales.order", domain, ["total_amount:avg"], [])
        const prev_average = await this.orm.readGroup("liquor_store.sales.order", prev_domain, ["total_amount:avg"], [])
        const average_percentage = ((current_average[0].total_amount - prev_average[0].total_amount) / prev_average[0].total_amount) * 100

        this.state.orders = {
            value: data,
            percentage: percentage.toFixed(2),
            revenue: `${(current_revenue[0].total_amount/1000).toFixed(2)}K`,
            revenue_percentage: revenue_percentage.toFixed(2),
            average: `${(current_average[0].total_amount/1000).toFixed(2)}K`,
            average_percentage: average_percentage.toFixed(2),
        }

     
    }

    async viewQuotations(){
        let domain = [['state', 'in', ['sent', 'draft']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'view_quotation_tree_with_onboarding']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "sale.order",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    viewOrders(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "sale.order",
            domain,
            context: {group_by: ['date_order']},
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }

    viewRevenues(){
        let domain = [['state', 'in', ['sale', 'done']]]
        if (this.state.period > 0){
            domain.push(['date_order','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Quotations",
            res_model: "sale.order",
            domain,
            context: {group_by: ['date_order']},
            views: [
                [false, "pivot"],
                [false, "form"],
            ]
        })
    }
}

OwlSalesDashboard.template = "owl.OwlSalesDashboard"
OwlSalesDashboard.components = { KpiCard, ChartRenderer }

registry.category("actions").add("owl.sales_dashboard", OwlSalesDashboard)